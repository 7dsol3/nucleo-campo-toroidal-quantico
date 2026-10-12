/* Offline V2 SI/RMS. Full driven-coil field, classical passive circuit. */
(function (root) {
  'use strict';
  const BASE = {"schema_version":"2.0","units":"SI; phasor voltages/currents/fields are RMS; z measured from base plane","config":{"schema_version":"2.0","geometry":{"coil_mean_radius_m":0.1,"coil_center_lower_m":0.065,"coil_center_upper_m":0.185,"radial_layers":5,"turns_per_layer":10,"wire_bare_diameter_m":0.001,"wire_pitch_m":0.0011,"coil_leads_each_m":0.4,"temperature_c":20,"copper_resistivity_20c_ohm_m":1.724e-08,"copper_temperature_coefficient_per_c":0.00393},"circuit":{"frequency_hz":1400,"capacitor_each_f":1e-05,"series_resistor_each_ohm":10,"series_resistor_rating_w":10,"capacitor_rating_v":100,"source_max_rms_v":5,"current_limit_rms_a":0.5,"drives":[{"voltage_rms_v":2,"phase_deg":0,"orientation":1},{"voltage_rms_v":2,"phase_deg":0,"orientation":1}]},"receiver":{"enabled":true,"radius_m":0.035,"center_z_m":0.125,"turns":20,"leads_m":0.4,"load_ohm":100,"load_rating_w":0.25,"axial_length_m":0.0055,"radial_depth_m":0.0044,"orientation":1},"toroidal":{"enabled":false,"turns":48,"major_radius_m":0.135,"minor_radius_m":0.008,"center_z_m":0.125,"drive_current_rms_a":0.15,"phase_deg":0,"leads_m":0.4},"control_cc":{"target_a":0.15,"kp_ohm":8,"ki_ohm_per_s":800,"duration_s":0.4,"step_s":1e-06},"numerics":{"mutual_angular_samples":512,"field_angular_samples":128,"toroid_angular_samples":64,"axis_points":81,"slice_points_per_dimension":25,"sweep_points":161}},"parameters":{"turns_each":50,"self_inductance_each_h":0.0010442991708264583,"mutual_inductance_h":9.345137205654844e-05,"receiver_inductance_h":5.085031586867128e-05,"mutual_to_receiver_h":[1.504895830179913e-05,1.504895830179913e-05],"coupling_coefficient":0.08948716485390966,"inductance_matrix_h":[[0.0010442991708264583,9.345137205654844e-05,1.504895830179913e-05],[9.345137205654844e-05,0.0010442991708264583,1.504895830179913e-05],[1.504895830179913e-05,1.504895830179913e-05,5.085031586867128e-05]],"inductance_matrix_physical_h":[[0.0010442991708264583,9.345137205654844e-05,1.504895830179913e-05],[9.345137205654844e-05,0.0010442991708264583,1.504895830179913e-05],[1.504895830179913e-05,1.504895830179913e-05,5.085031586867128e-05]],"matrix_positive_definite":true,"orientations":[1,1,1],"copper_resistance_each_ohm":[0.6983802599004937,0.6983802599004937],"receiver_copper_resistance_ohm":0.1053242599004937,"wire_length_each_m":[31.81592653589793,31.81592653589793],"receiver_wire_length_m":4.798229715025711,"winding_axial_length_m":0.011000000000000001,"winding_radial_depth_m":0.0055000000000000005,"resistance_each_ohm":[10.698380259900494,10.698380259900494],"resonance_symmetric_unloaded_hz":1492.09544967752,"resonance_antisymmetric_unloaded_hz":1632.167135708757,"quality_symmetric_unloaded":0.9970237309953927,"skin_depth_m":0.001766138446074769,"self_inductance_method":"Wheeler multilayer estimate; measure before matching resonances","mutual_method":"Neumann distributed 50 loops per drive, receiver 20 coincident mean-radius loops"},"circuit":{"frequency_hz":1400,"source_voltages":[{"re":2.0,"im":0.0,"rms":2.0,"phase_deg":0.0},{"re":2.0,"im":0.0,"rms":2.0,"phase_deg":0.0}],"currents":[{"re":0.18396522896585982,"im":0.023385878107873445,"rms":0.1854456922210315,"phase_deg":7.244650184171786},{"re":0.18396522896585982,"im":0.023385878107873445,"rms":0.1854456922210315,"phase_deg":7.244650184171786},{"re":5.9674932033042316e-05,"im":-0.00048681152717330265,"rms":0.0004904554623020844,"phase_deg":-83.01136405706492}],"physical_currents":[{"re":0.18396522896585982,"im":0.023385878107873445,"rms":0.1854456922210315,"phase_deg":7.244650184171786},{"re":0.18396522896585982,"im":0.023385878107873445,"rms":0.1854456922210315,"phase_deg":7.244650184171786},{"re":5.9674932033042316e-05,"im":-0.00048681152717330265,"rms":0.0004904554623020844,"phase_deg":-83.01136405706492}],"capacitor_voltages":[{"re":0.2658555785294714,"im":-2.091355396210637,"rms":2.1081856137196717,"phase_deg":-82.75534981582821},{"re":0.2658555785294714,"im":-2.091355396210637,"rms":2.1081856137196717,"phase_deg":-82.75534981582821}],"receiver_load_voltage":{"re":0.005967493203304232,"im":-0.04868115271733026,"rms":0.049045546230208445,"phase_deg":-83.01136405706492},"power":{"source_each_w":[0.36793045793171963,0.36793045793171963],"source_reactive_each_var":[-0.04677175621574689,-0.04677175621574689],"source_total_w":0.7358609158634393,"copper_each_w":[0.02401737030262488,0.02401737030262488],"series_resistor_each_w":[0.3439010476333754,0.3439010476333754],"receiver_copper_w":2.5335388456477354e-08,"receiver_load_w":2.4054656050195133e-05,"dissipation_total_w":0.7358609158634393,"balance_residual_w":0.0,"transfer_efficiency":3.2689133954029955e-05},"energy":{"mean_magnetic_j":3.9127354248356465e-05,"mean_capacitive_each_j":[2.2222232909472946e-05,2.2222232909472946e-05]},"validity":{"linear_region":true,"warnings":[],"source_port_requirement":"two independently phase-controlled isolated sine outputs; specified RMS amplitude under actual load; 50-ohm function-generator amplitude labels are insufficient"}},"center_point_m":[0.0,0.0,0.125],"center_field":{"components_t":[{"re":0.0,"im":0.0,"rms":0.0,"phase_deg":0.0},{"re":0.0,"im":0.0,"rms":0.0,"phase_deg":0.0},{"re":7.291903142642153e-05,"im":9.092045709972222e-06,"rms":7.348367464518684e-05,"phase_deg":7.107350593549778}],"magnitude_rms_t":7.348367464518684e-05,"ellipse_major_peak_t":0.00010392160929623517,"ellipse_minor_peak_t":9.094947017729282e-13,"mean_magnetic_energy_density_j_m3":0.0021485322234525883},"toroidal":{"enabled":false,"turns":48,"wire_length_m":2.812743157956961,"copper_resistance_dc_ohm":0.061741539900493685,"self_inductance_ideal_h":6.862913871522022e-07,"ideal_bulk_field_rms_t":0.0,"drive_current_rms_a":0.0,"required_voltage_estimate_rms_v":0.0,"copper_loss_w":0.0,"qualification":"Independent ideal current-driven air-core toroid. L and voltage estimates use ideal bulk approximation, whereas field uses actual poloidal loop geometry. Leakage, parasitic capacitance, winding leads and toroid-to-drive mutual are not included in this circuit; optional toroid results are separate from axial transfer power balance."},"control_cc":{"mode":"Separate DC RL bench with capacitors bypassed, receiver disconnected, two equal axially aiding ports; not an AC amplitude controller","effective_inductance_per_port_h":0.0011377505428830067,"target_a":0.15,"final_current_a":0.1499977726883678,"max_current_a":0.15038058465017673,"absolute_final_error_a":2.2273116321858133e-06,"voltage_limit_v":5,"disturbance_ohm":1.0,"step_s":1e-06,"stable_linear_no_clipping":true,"controller_saturation_is_voltage_only":true},"energy_curvature_scale":{"local_mean_magnetic_energy_density_j_m3":0.0021485322234525883,"einstein_tensor_magnetic_order_m_inv2":4.461743947702839e-46,"meaning":"Local order of Einstein tensor sourced by mean classical magnetic energy only. Not Ricci scalar, not a computed spacetime metric. Maxwell stress-energy is traceless: R=0 in electrovacuum with Lambda=0. Electric energy and other stresses are not included in this local scale."},"status":"CLASSICAL_NUMERICAL_PREDICTION_NOT_EXPERIMENTAL_CONFIRMATION","missing_physics":["No vacuum energy extraction law","No wormhole mechanism","No reactionless thrust","No quantum coherence or quantum-state evolution","No practical controllable spacetime curvature"]};
  const MU0 = 4 * Math.PI * 1e-7;
  const cfg = BASE.config;
  const original = BASE.parameters;
  const fieldCache = new Map();
  const torusCache = new Map();
  const angleCache = new Map();
  const add = (a,b) => [a[0]+b[0], a[1]+b[1]];
  const sub = (a,b) => [a[0]-b[0], a[1]-b[1]];
  const mul = (a,b) => [a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]];
  const scale = (a,s) => [a[0]*s,a[1]*s];
  const abs = a => Math.hypot(a[0],a[1]);
  const div = (a,b) => { const den=b[0]*b[0]+b[1]*b[1]; if(den<1e-36) throw new Error('Singular circuit'); return [(a[0]*b[0]+a[1]*b[1])/den,(a[1]*b[0]-a[0]*b[1])/den]; };
  const phasor = a => ({re:a[0],im:a[1],rms:abs(a),phase_deg:Math.atan2(a[1],a[0])*180/Math.PI});
  const from = a => [a.re,a.im];
  const defaults = {
    frequency_hz:cfg.circuit.frequency_hz,voltage_lower:cfg.circuit.drives[0].voltage_rms_v,
    voltage_upper:cfg.circuit.drives[1].voltage_rms_v,phase_lower_deg:cfg.circuit.drives[0].phase_deg,phase_upper_deg:cfg.circuit.drives[1].phase_deg,
    orientation_lower:cfg.circuit.drives[0].orientation,
    orientation_upper:cfg.circuit.drives[1].orientation,receiver_enabled:cfg.receiver.enabled,
    load_ohm:cfg.receiver.load_ohm,temperature_c:cfg.geometry.temperature_c,
    toroid_enabled:cfg.toroidal.enabled,toroid_current_rms_a:cfg.toroidal.drive_current_rms_a,
    toroid_phase_deg:cfg.toroidal.phase_deg
  };
  function inputState(input={}) {
    const x={...defaults,...input};
    for(const name of ['frequency_hz','voltage_lower','voltage_upper','phase_lower_deg','phase_upper_deg','load_ohm','temperature_c','toroid_current_rms_a','toroid_phase_deg']) {
      if(!Number.isFinite(x[name])) throw new Error('Non-finite '+name);
    }
    if(x.frequency_hz<=0 || x.load_ohm<=0 || x.voltage_lower<0 || x.voltage_upper<0 || Math.max(x.voltage_lower,x.voltage_upper)>cfg.circuit.source_max_rms_v || ![-1,1].includes(x.orientation_upper) || ![-1,1].includes(x.orientation_lower) || x.toroid_current_rms_a<0) throw new Error('Input outside prototype range');
    if(1+cfg.geometry.copper_temperature_coefficient_per_c*(x.temperature_c-20)<=0) throw new Error('Temperature outside linear copper model');
    return x;
  }
  function gauss(matrix,rhs) {
    const n=rhs.length;
    const a=matrix.map((row,i)=>[...row.map(v=>[...v]),[...rhs[i]]]);
    for(let j=0;j<n;j++) {
      let pivot=j;
      for(let i=j+1;i<n;i++) if(abs(a[i][j])>abs(a[pivot][j])) pivot=i;
      [a[j],a[pivot]]=[a[pivot],a[j]];
      const diagonal=[...a[j][j]];
      a[j]=a[j].map(v=>div(v,diagonal));
      for(let i=0;i<n;i++) if(i!==j) {
        const factor=[...a[i][j]];
        a[i]=a[i].map((v,k)=>sub(v,mul(factor,a[j][k])));
      }
    }
    return a.map(row=>row[n]);
  }
  function solve(input={}) {
    const x=inputState(input), c=cfg.circuit,rx=cfg.receiver;
    const n=x.receiver_enabled?3:2,w=2*Math.PI*x.frequency_hz;
    const orientations=[x.orientation_lower,x.orientation_upper,rx.orientation];
    // Base physical L matrix contains unsigned reference +z winding axes.
    const physicalL=[[original.self_inductance_each_h,original.mutual_inductance_h,original.mutual_to_receiver_h[0]],
      [original.mutual_inductance_h,original.self_inductance_each_h,original.mutual_to_receiver_h[1]],
      [original.mutual_to_receiver_h[0],original.mutual_to_receiver_h[1],original.receiver_inductance_h]];
    const L=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>physicalL[i][j]*orientations[i]*orientations[j]));
    const rhoRatio=(1+cfg.geometry.copper_temperature_coefficient_per_c*(x.temperature_c-20))/(1+cfg.geometry.copper_temperature_coefficient_per_c*(cfg.geometry.temperature_c-20));
    const copper=original.copper_resistance_each_ohm.map(r=>r*rhoRatio);
    const rxCopper=original.receiver_copper_resistance_ohm*rhoRatio;
    const matrix=L.map(row=>row.map(value=>[0,w*value]));
    for(let i=0;i<2;i++) matrix[i][i]=add(matrix[i][i],[c.series_resistor_each_ohm+copper[i],-1/(w*c.capacitor_each_f)]);
    if(n===3) matrix[2][2]=add(matrix[2][2],[rxCopper+x.load_ohm,0]);
    const phase=x.phase_upper_deg*Math.PI/180;
    const lowerPhase=x.phase_lower_deg*Math.PI/180;
    const source=[[x.voltage_lower*Math.cos(lowerPhase),x.voltage_lower*Math.sin(lowerPhase)],[x.voltage_upper*Math.cos(phase),x.voltage_upper*Math.sin(phase)]];
    const currents=gauss(matrix,n===3?[...source,[0,0]]:source);
    const physicalCurrents=currents.map((i,k)=>scale(i,orientations[k]));
    const complexP=source.map((v,k)=>mul(v,[currents[k][0],-currents[k][1]]));
    const sourceP=complexP.map(p=>p[0]);
    const copperP=copper.map((r,i)=>abs(currents[i])**2*r);
    const seriesP=currents.slice(0,2).map(i=>abs(i)**2*c.series_resistor_each_ohm);
    const receiverCopper=n===3?abs(currents[2])**2*rxCopper:0;
    const receiverLoad=n===3?abs(currents[2])**2*x.load_ohm:0;
    const sourceTotal=sourceP.reduce((a,b)=>a+b,0);
    const dissipation=copperP.reduce((a,b)=>a+b,0)+seriesP.reduce((a,b)=>a+b,0)+receiverCopper+receiverLoad;
    const capV=currents.slice(0,2).map(i=>div(i,[0,w*c.capacitor_each_f]));
    const warnings=[];
    if(Math.max(...currents.slice(0,2).map(abs))>c.current_limit_rms_a) warnings.push('CURRENT_LIMIT_EXCEEDED');
    if(seriesP.some(v=>v>c.series_resistor_rating_w)) warnings.push('SERIES_RESISTOR_POWER_EXCEEDED');
    if(capV.some(v=>Math.SQRT2*abs(v)>c.capacitor_rating_v)) warnings.push('CAPACITOR_PEAK_VOLTAGE_EXCEEDED');
    if(receiverLoad>rx.load_rating_w) warnings.push('RECEIVER_LOAD_POWER_EXCEEDED');
    if(sourceP.some(v=>v< -1e-10)) warnings.push('SOURCE_ABSORBS_REAL_POWER');
    let magnetic=0;
    for(let i=0;i<n;i++) for(let j=0;j<n;j++) magnetic+=.5*L[i][j]*mul([currents[i][0],-currents[i][1]],currents[j])[0];
    return {input:x,frequency_hz:x.frequency_hz,source_voltages:source.map(phasor),currents:currents.map(phasor),physical_currents:physicalCurrents.map(phasor),
      capacitor_voltages:capV.map(phasor),receiver_load_voltage:phasor(n===3?scale(currents[2],x.load_ohm):[0,0]),
      power:{source_each_w:sourceP,source_reactive_each_var:complexP.map(p=>p[1]),source_total_w:sourceTotal,copper_each_w:copperP,
        series_resistor_each_w:seriesP,receiver_copper_w:receiverCopper,receiver_load_w:receiverLoad,dissipation_total_w:dissipation,
        balance_residual_w:sourceTotal-dissipation,transfer_efficiency:sourceTotal>0?receiverLoad/sourceTotal:0},
      energy:{mean_magnetic_j:magnetic,mean_capacitive_each_j:capV.map(v=>.5*c.capacitor_each_f*abs(v)**2)},
      validity:{linear_region:warnings.length===0,warnings},parameters:{...original,inductance_matrix_h:L,copper_resistance_each_ohm:copper,receiver_copper_resistance_ohm:rxCopper}};
  }
  function angles(count) {
    if(!angleCache.has(count)) angleCache.set(count,Array.from({length:count},(_,k)=>{const a=(k+.5)*2*Math.PI/count;return [Math.cos(a),Math.sin(a)];}));
    return angleCache.get(count);
  }
  function loopField(radius,center,point,count=128) {
    const [x,y,z]=point,dz=z-center;
    if(Math.hypot(Math.hypot(x,y)-radius,dz)<=cfg.geometry.wire_bare_diameter_m/2) throw new Error('FIELD_IN_WIRE_EXCLUDED');
    if(x*x+y*y<1e-28) return [0,0,MU0*radius*radius/(2*(radius*radius+dz*dz)**1.5)];
    const out=[0,0,0],step=2*Math.PI/count;
    for(const [cosine,sine] of angles(count)) {
      const dx=x-radius*cosine,dy=y-radius*sine;
      const factor=MU0/(4*Math.PI)*radius*step/(dx*dx+dy*dy+dz*dz)**1.5;
      out[0]+=cosine*dz*factor;out[1]+=sine*dz*factor;out[2]+=(radius-x*cosine-y*sine)*factor;
    }
    return out;
  }
  function storeCache(cache,key,value) {if(cache.size>20000) cache.clear();cache.set(key,value);return value;}
  function unitBasis(point) {
    const key=point.join(','); if(fieldCache.has(key)) return fieldCache.get(key);
    const g=cfg.geometry,rx=cfg.receiver,fields=[];
    for(const center of [g.coil_center_lower_m,g.coil_center_upper_m]) {
      const out=[0,0,0];
      for(let j=0;j<g.radial_layers;j++) for(let k=0;k<g.turns_per_layer;k++) {
        const radius=g.coil_mean_radius_m+(j-(g.radial_layers-1)/2)*g.wire_pitch_m;
        const z=center+(k-(g.turns_per_layer-1)/2)*g.wire_pitch_m;
        const b=loopField(radius,z,point,cfg.numerics.field_angular_samples);
        for(let axis=0;axis<3;axis++) out[axis]+=b[axis];
      }
      fields.push(out);
    }
    if(Math.abs(Math.hypot(point[0],point[1])-rx.radius_m)<=rx.radial_depth_m/2 && Math.abs(point[2]-rx.center_z_m)<=rx.axial_length_m/2) fields.push(null);
    else fields.push(loopField(rx.radius_m,rx.center_z_m,point,cfg.numerics.field_angular_samples).map(v=>v*rx.turns));
    return storeCache(fieldCache,key,fields);
  }
  function torusBasis(point) {
    const key=point.join(',');if(torusCache.has(key)) return torusCache.get(key);
    const t=cfg.toroidal,R=t.major_radius_m,r=t.minor_radius_m,count=cfg.numerics.toroid_angular_samples,step=2*Math.PI/count,out=[0,0,0];
    for(let turn=0;turn<t.turns;turn++) {
      const phi=2*Math.PI*turn/t.turns,cp=Math.cos(phi),sp=Math.sin(phi);
      const radial=point[0]*cp+point[1]*sp,normal=-point[0]*sp+point[1]*cp;
      if(Math.hypot(Math.hypot(radial-R,point[2]-t.center_z_m)-r,normal)<=cfg.geometry.wire_bare_diameter_m/2) throw new Error('FIELD_IN_TOROID_WIRE_EXCLUDED');
      for(const [ct,st] of angles(count)) {
        const dx=point[0]-(R+r*ct)*cp,dy=point[1]-(R+r*ct)*sp,dz=point[2]-(t.center_z_m-r*st);
        const dl=[-r*st*cp*step,-r*st*sp*step,-r*ct*step];
        const factor=MU0/(4*Math.PI)/(dx*dx+dy*dy+dz*dz)**1.5;
        out[0]+=(dl[1]*dz-dl[2]*dy)*factor;out[1]+=(dl[2]*dx-dl[0]*dz)*factor;out[2]+=(dl[0]*dy-dl[1]*dx)*factor;
      }
    }
    return storeCache(torusCache,key,out);
  }
  function fieldSummary(vector) {
    const norm2=vector.reduce((n,b)=>n+b[0]*b[0]+b[1]*b[1],0);
    const q=vector.reduce((sum,b)=>add(sum,mul(b,b)),[0,0]);
    return {real:vector.map(b=>b[0]),imag:vector.map(b=>b[1]),components_t:vector.map(phasor),rms_norm_t:Math.sqrt(norm2),magnitude_rms_t:Math.sqrt(norm2),
      ellipse_major_peak_t:Math.sqrt(Math.max(0,norm2+abs(q))),ellipse_minor_peak_t:Math.sqrt(Math.max(0,norm2-abs(q))),mean_magnetic_energy_density_j_m3:norm2/(2*MU0)};
  }
  function torusFieldAt(point,input={}) {
    const x=inputState(input),basis=torusBasis(point),phase=x.toroid_phase_deg*Math.PI/180,current=x.toroid_enabled?x.toroid_current_rms_a:0;
    return fieldSummary(basis.map(v=>[v*current*Math.cos(phase),v*current*Math.sin(phase)]));
  }
  function fieldAt(point,input={},result) {
    if(!Array.isArray(point)||point.length!==3||point.some(p=>!Number.isFinite(p))) throw new Error('Point must contain three SI coordinates');
    const solution=result||solve(input),x=solution.input||inputState(input),basis=unitBasis(point),out=[[0,0],[0,0],[0,0]];
    solution.physical_currents.forEach((current,i)=>{
      if(basis[i]===null) throw new Error('FIELD_IN_RECEIVER_ENVELOPE_EXCLUDED');
      for(let k=0;k<3;k++) out[k]=add(out[k],scale(from(current),basis[i][k]));
    });
    if(x.toroid_enabled) {
      const toroidal=torusFieldAt(point,x);
      for(let k=0;k<3;k++) out[k]=add(out[k],[toroidal.real[k],toroidal.imag[k]]);
    }
    return fieldSummary(out);
  }
  const api={solve,fieldAt,torusFieldAt,defaults:{...defaults},config:cfg,baseline:BASE,unitBasis,torusBasis,clearCache:()=>{fieldCache.clear();torusCache.clear();}};
  root.NucleoPhysics=api;
  if(typeof module!=='undefined'&&module.exports) module.exports=api;
})(typeof window!=='undefined'?window:globalThis);
