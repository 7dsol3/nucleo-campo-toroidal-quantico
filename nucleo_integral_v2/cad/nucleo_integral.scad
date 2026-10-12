// Núcleo integral V2 — modelo mecânico proposto. Unidades mm.
// Bobinas convencionais, ar comum, fonte externa. Sem peças de pressão/vácuo.
// Roscas, componentes eletrônicos e conexões do fio são simplificadas.
$fn=128;
modo="montagem"; // montagem, base, carretel, tampa, ponte, receptor, toroide, pedestal
R=100; N=50; diam_fio=1.1;
centros=[65,185]; R_tirante=155;
module anel(ri,ro,h){difference(){cylinder(h=h,r=ro);translate([0,0,-.1])cylinder(h=h+.2,r=ri);}}
module furos(r,d,h){for(a=[45:90:315])translate([r*cos(a),r*sin(a),-.1])cylinder(h=h+.2,d=d);}
module base(){difference(){translate([-180,-180,0])cube([360,360,12]);furos(155,5.5,12);}}
module tampa(){difference(){anel(124,170,4);furos(155,5.5,4);}}
module carretel(){difference(){union(){anel(94,110,2);translate([0,0,13.4])anel(94,110,2);translate([0,0,2])anel(95.25,97.25,11.4);}furos(107,3.4,15.4);}}
module ponte(){difference(){translate([104,-6,0])cube([56,12,4.3]);for(v=[[107,3.4],[155,5.5]])translate([v[0],0,-.1])cylinder(h=4.5,d=v[1]);}}
module receptor(){union(){anel(31,40,3);translate([0,0,9])anel(31,40,3);translate([0,0,3])anel(31,32.5,6);}}
module toroide(rminor=6.5){rotate_extrude()translate([135,0,0])circle(r=rminor);}
module pedestal(){anel(5,35,10);}
module porca(ri=2.5,af=8,h=4){difference(){cylinder(h=h,r=af/sqrt(3),$fn=6);translate([0,0,-.1])cylinder(h=h+.2,r=ri);}}
module montagem(){
  color([.22,.28,.34])base();
  for(i=[0:1])let(z=centros[i]){
    color(i==0?[.86,.31,.1]:[.11,.43,.68])for(z0=[z-16,z+12])translate([0,0,z0])tampa();
    color(i==0?[.86,.31,.1]:[.11,.43,.68])for(a=[22.5:45:337.5])translate([160*cos(a),160*sin(a),z-12])rotate([0,0,a])translate([-10,-5,0])cube([20,10,24]);
    color([.75,.83,.87])for(a=[45:90:315],z0=[z-12,z+7.7])translate([0,0,z0])rotate([0,0,a])ponte();
    color([.14,.2,.26])translate([0,0,z-7.7])carretel();
    color([.88,.44,.16])translate([0,0,z-5.5])anel(97.25,102.75,11);
    color([.75,.83,.87])for(a=[45:90:315])translate([107*cos(a),107*sin(a),z-15]){
      cylinder(h=31,d=3);
      for(hh=[2.5,27])translate([0,0,hh])anel(1.7,3,.5);
      for(hh=[.1,27.5])translate([0,0,hh])porca(1.5,5.5,2.4);
    }
  }
  color([.75,.83,.87])for(a=[45:90:315])translate([155*cos(a),155*sin(a),0]){
    translate([0,0,-5])cylinder(h=231,d=5);
    for(pair=[[12,49],[57.3,72.7],[81,169],[177.3,192.7],[201,218]])translate([0,0,pair[0]])anel(2.75,5,pair[1]-pair[0]);
    for(z=[-1,218])translate([0,0,z])anel(2.75,5,1);
    for(z=[-5,219])translate([0,0,z])porca();
  }
  color([.25,.76,.9,.24])translate([0,0,22])anel(25,27,198);
  color([.14,.2,.26])translate([0,0,12])pedestal();
  color([.11,.43,.68])for(z=[22,214])translate([0,0,z])anel(27.3,35,6);
  color([.75,.83,.87])translate([0,0,12])cylinder(h=111,d=8);
  color([.14,.2,.26])translate([0,0,119])receptor();
  color([.88,.44,.16])translate([0,0,122.25])anel(32.8,37.2,5.5);
  color([.11,.43,.68])translate([0,0,115])anel(27.3,31,2);
  color([.75,.83,.87])for(a=[0:90:270])translate([0,0,117])rotate([0,0,a])translate([29,-3,0])cube([9,6,2]);
  color([.14,.2,.26])translate([0,0,125])toroide();
  color([.11,.43,.68])translate([0,0,125])difference(){toroide(7.45);toroide(6.5);}
  color([.88,.44,.16])for(a=[0:7.5:352.5])rotate([0,0,a])translate([135,0,125])rotate([90,0,0])rotate_extrude($fn=40)translate([8,0])circle(r=.55,$fn=8);
  color([.75,.83,.87])for(a=[3.75:90:273.75])translate([135*cos(a),135*sin(a),81])cylinder(h=36.55,d=8);
  color([.04,.06,.09])for(x=[-155,155],y=[-155,155])translate([x,y,-8])cylinder(h=8,d=16);
  color([.14,.2,.26])translate([-165,-165,12])difference(){cube([80,60,28]);translate([2,2,2])cube([76,56,27]);}
  color([.11,.43,.68])for(k=[0:4])translate([-163,-163+11*k,40])cube([76,5,2]);
  color([.09,.4,.27])translate([-160,-160,17])cube([40,49,2]);
  color([.86,.31,.1])translate([-113,-150,18])cube([21,29,8]);
  color([.75,.83,.87])translate([-163,-152,23])cube([7,16,11]);
  color([.66,.28,.77]){
    translate([-2,-2,123])cube([4,4,4]);
    for(z=centros)translate([102.75,-2,z-2])cube([4,4,4]);
  }
}
if(modo=="montagem")montagem();
if(modo=="base")base();if(modo=="carretel")carretel();
if(modo=="tampa")tampa();if(modo=="ponte")ponte();
if(modo=="receptor")receptor();if(modo=="toroide")toroide();if(modo=="pedestal")pedestal();
