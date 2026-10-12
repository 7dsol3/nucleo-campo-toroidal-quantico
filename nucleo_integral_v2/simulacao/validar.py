"""Verificações físicas e paridade com o motor offline em Chrome real.

py validar.py --browser
Esses testes verificam código/modelo; não são ensaios de um aparelho físico.
"""
import argparse
import copy
import json
import math
from pathlib import Path
import modelo_integral as m

ROOT=Path(__file__).resolve().parent
import sys
sys.path.insert(0,str(ROOT.parent))
from browser_runtime import launch_browser


def validate(browser=False):
    c=m.load_config()
    p=m.parameters(c)
    s=m.circuit_solution(c,p)
    checks=[]
    def check(name,passed,**details):
        checks.append({'name':name,'passed':bool(passed),**details})
    def close(actual,wanted,rel=1e-10,absolute=1e-15):
        return abs(actual-wanted)<=max(absolute,abs(wanted)*rel)
    # Closed-form on-axis circular loop: independent analytic benchmark.
    for r,d in [(.1,.06),(.035,.11),(.135,0)]:
        actual=m.loop_field_per_a(r,0,(0,0,d),512,0.0005)[2]
        expected=m.MU0*r*r/(2*(r*r+d*d)**1.5)
        check(f'analytic_axis_{r}_{d}',close(actual,expected),actual=actual,expected=expected)
    # Coaxial small-receiver limit = area × analytic on-axis field per ampere.
    small=m.mutual_loop_h(.1,.0002,.2,1024)
    flux_limit=math.pi*.0002**2*m.loop_axis_b_per_a(.1,.2)
    check('mutual_small_loop_flux_limit',close(small,flux_limit,rel=3e-6),relative_error=abs(small-flux_limit)/flux_limit)
    check('mutual_reciprocity',close(m.mutual_loop_h(.1,.035,.06),m.mutual_loop_h(.035,.1,.06)))
    packs=[m.winding_loops(c['geometry'],z) for z in [.065,.185]]
    finer=m.distributed_mutual_h(*packs,1024)
    check('mutual_quadrature_convergence',close(finer,p['mutual_inductance_h'],rel=1e-10),relative_error=abs(finer-p['mutual_inductance_h'])/finer)
    check('energy_positive_inductance_matrix',m.positive_definite(p['inductance_matrix_h']))
    check('baseline_valid_region',s['validity']['linear_region'],warnings=s['validity']['warnings'])
    for phase in [0,37,90,180]:
        for orientation in [1,-1]:
            conf=copy.deepcopy(c)
            conf['circuit']['drives'][1]['phase_deg']=phase
            conf['circuit']['drives'][1]['orientation']=orientation
            sol=m.circuit_solution(conf)
            power=sol['power']
            check(f'power_balance_phase_{phase}_sense_{orientation}',abs(power['balance_residual_w'])<2e-13,residual_w=power['balance_residual_w'])
            check(f'passive_receiver_phase_{phase}_sense_{orientation}',power['receiver_load_w']<=power['source_total_w']+1e-13)
    conf=copy.deepcopy(c)
    conf['circuit']['drives'][1]['phase_deg']=180
    anti=m.circuit_solution(conf)
    anti_b=m.field_solution(conf,anti,(0,0,.125))['magnitude_rms_t']
    check('antisymmetric_center_field_cancels',anti_b<1e-16,field_t=anti_b)
    check('antisymmetric_receiver_emf_cancels',anti['currents'][2]['rms']<1e-14,current_a=anti['currents'][2]['rms'])
    conf=copy.deepcopy(c)
    for d in conf['circuit']['drives']:d['voltage_rms_v']=0
    zero=m.circuit_solution(conf)
    check('no_source_no_output',all(i['rms']==0 for i in zero['currents']) and zero['power']['receiver_load_w']==0)
    conf=copy.deepcopy(c)
    conf['receiver']['enabled']=False
    unloaded=m.circuit_solution(conf)
    check('receiver_disconnect_two_port',len(unloaded['currents'])==2 and unloaded['power']['receiver_load_w']==0)
    # Maxwell div B = 0 in an empty off-axis region, centered difference.
    point=[.04,.015,.14]
    h=1e-5
    derivative=0.0
    for axis in range(3):
        left=list(point);right=list(point)
        left[axis]-=h;right[axis]+=h
        bl=m.field_solution(c,s,left)['components_t'][axis]['re']
        br=m.field_solution(c,s,right)['components_t'][axis]['re']
        derivative+=(br-bl)/(2*h)
    field=m.field_solution(c,s,point)['magnitude_rms_t']
    relative=abs(derivative)/(field/.1)
    check('maxwell_divergence_empty_space',relative<2e-5,relative_divergence=relative)
    conf=copy.deepcopy(c)
    conf['circuit']['drives'][1]['phase_deg']=90
    elliptical=m.field_solution(conf,m.circuit_solution(conf),(.045,.013,.12))
    check('phase_shift_elliptical_vector',elliptical['ellipse_minor_peak_t']>0 and elliptical['ellipse_minor_peak_t']<=elliptical['ellipse_major_peak_t'])
    # True toroidal field: exact rotational covariance and grid convergence.
    t=c['toroidal'];R=t['major_radius_m'];z=t['center_z_m']
    tor=m.toroidal_field_per_a(c,(R,0,z),64)
    tor_fine=m.toroidal_field_per_a(c,(R,0,z),128)
    check('toroid_segment_convergence',all(close(a,b,rel=1e-10,absolute=1e-17) for a,b in zip(tor,tor_fine)))
    angle=2*math.pi/t['turns']
    rot=m.toroidal_field_per_a(c,(R*math.cos(angle),R*math.sin(angle),z))
    expected=[tor[0]*math.cos(angle)-tor[1]*math.sin(angle),tor[0]*math.sin(angle)+tor[1]*math.cos(angle),tor[2]]
    check('toroid_discrete_rotational_symmetry',all(close(a,b,rel=1e-9,absolute=1e-17) for a,b in zip(rot,expected)))
    axial=m.toroidal_field_per_a(c,(0,0,z))
    check('toroid_axis_cancelled',math.hypot(*axial)<1e-17)
    # Ampère line integral over circle inside torus. Azimuth midpoint quadrature.
    # Discrete ripple is allowed; average must match mu0*N*I.
    ampere=0.0
    samples=192
    for k in range(samples):
        phi=2*math.pi*(k+.5)/samples
        b=m.toroidal_field_per_a(c,(R*math.cos(phi),R*math.sin(phi),z))
        ampere+=(-math.sin(phi)*b[0]+math.cos(phi)*b[1])*R*2*math.pi/samples
    expected=m.MU0*t['turns']
    check('toroid_ampere_law',close(ampere,expected,rel=.002),relative_error=abs(ampere-expected)/expected)
    try:
        m.loop_field_per_a(.1,.065,(.1,0,.065))
        excluded=False
    except ValueError:
        excluded=True
    check('wire_singularity_explicitly_excluded',excluded)
    ctl=m.control_cc(c,p)
    check('dc_controller_disturbance_recovery',ctl['absolute_final_error_a']<1e-5,error_a=ctl['absolute_final_error_a'])
    check('dc_controller_physical_limits',ctl['max_current_a']<c['circuit']['current_limit_rms_a'] and max(r[2] for r in ctl['rows'])<=c['circuit']['source_max_rms_v'])
    ctrl_fine=copy.deepcopy(c)
    ctrl_fine['control_cc']['step_s']/=2
    second=m.control_cc(ctrl_fine,p)
    check('dc_controller_step_convergence',abs(second['final_current_a']-ctl['final_current_a'])<1e-7,difference_a=abs(second['final_current_a']-ctl['final_current_a']))
    if browser:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            engine=launch_browser(pw,headless=True)
            page=engine.new_page()
            page.goto('about:blank')
            page.add_script_tag(path=str(ROOT/'modelo_browser.js'))
            # Compare independent language implementations for complex phases, load,
            # temperature, reversal and real toroid field at 3D points.
            for phase,orientation,receiver,temperature,load,toroid in [(0,1,True,20,100,False),(90,1,True,55,10,False),(180,1,True,20,100,False),(37,-1,False,20,100,True)]:
                conf=copy.deepcopy(c)
                conf['circuit']['drives'][1]['phase_deg']=phase
                conf['circuit']['drives'][1]['orientation']=orientation
                conf['geometry']['temperature_c']=temperature
                conf['receiver']['enabled']=receiver
                conf['receiver']['load_ohm']=load
                conf['toroidal']['enabled']=toroid
                actual_input={'phase_upper_deg':phase,'orientation_upper':orientation,'receiver_enabled':receiver,'temperature_c':temperature,'load_ohm':load,'toroid_enabled':toroid}
                reference=m.circuit_solution(conf)
                actual=page.evaluate('(input)=>NucleoPhysics.solve(input)',actual_input)
                suffix=f'{phase}_{orientation}_{receiver}_{temperature}_{load}_{toroid}'
                check('browser_currents_'+suffix,all(close(a[k],b[k],absolute=1e-14) for a,b in zip(actual['currents'],reference['currents']) for k in ['re','im','rms']))
                check('browser_power_'+suffix,all(close(actual['power'][k],reference['power'][k],absolute=1e-13) for k in ['source_total_w','receiver_load_w','balance_residual_w','receiver_copper_w']))
                for point in [[0,0,.125],[.03,.012,.11],[.133,0,.125]]:
                    ref=m.field_solution(conf,reference,point)
                    found=page.evaluate('([point,input])=>NucleoPhysics.fieldAt(point,input)',[point,actual_input])
                    error=math.sqrt(sum((found['real'][k]-ref['components_t'][k]['re'])**2+(found['imag'][k]-ref['components_t'][k]['im'])**2 for k in range(3)))
                    check('browser_field_'+suffix+'_'+str(point),error<max(1e-16,ref['magnitude_rms_t']*1e-10),absolute_error_t=error)
            engine.close()
    report={'scope':'Numerical/classical model QA, analytic and Maxwell benchmarks plus optional Chrome parity. No experimental measurement.','passed':all(x['passed'] for x in checks),'check_count':len(checks),'passed_count':sum(x['passed'] for x in checks),'browser_checked':browser,'checks':checks}
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--browser',action='store_true')
    parser.add_argument('--output',default=str(ROOT/'outputs'/'validacao_modelo.json'))
    args=parser.parse_args()
    result=validate(args.browser)
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['passed','check_count','passed_count','browser_checked']}))
    for check in result['checks']:
        if not check['passed']: print(json.dumps(check))
    raise SystemExit(0 if result['passed'] else 1)
