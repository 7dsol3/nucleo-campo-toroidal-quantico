// Bancada de duas bobinas circulares: unidades mm.
// Nenhuma previsão de energia de vácuo, propulsão ou curvatura do espaço-tempo.
// Espiras azimutais: NÃO é um solenoide toroidal. Roscas simplificadas.
$fn=128;
modo="montagem"; // montagem, bobina, base, espacador_inferior, espacador_meio
R=100; d_fio=1.1; N=50;
raio_flange=110; raio_furos=107; d_furo=3.4;
esp_flange=2; gap=11.4; h_bobina=2*esp_flange+gap;
centro_z=[60,160];
h_base=8; lado_base=260;
h_esp_inf=centro_z[0]-h_bobina/2-h_base;
h_esp_meio=centro_z[1]-centro_z[0]-h_bobina;
module anel(ri,ro,h) { difference(){cylinder(h=h,r=ro);translate([0,0,-0.1])cylinder(h=h+0.2,r=ri);} }
module furos(h){for(a=[45:90:315])translate([raio_furos*cos(a),raio_furos*sin(a),-0.1])cylinder(h=h+0.2,d=d_furo);}
module bobina(){difference(){union(){anel(94,raio_flange,esp_flange);translate([0,0,esp_flange+gap])anel(94,raio_flange,esp_flange);translate([0,0,esp_flange])anel(95.25,97.25,gap);}furos(h_bobina);}}
module base(){difference(){translate([-lado_base/2,-lado_base/2,0])cube([lado_base,lado_base,h_base]);furos(h_base);}}
module espacador(h){anel(d_furo/2,3,h);}
module montagem(){
  color([0.65,0.74,0.8])base();
  for(z=centro_z){color([0.2,0.25,0.29])translate([0,0,z-h_bobina/2])bobina();color([0.78,0.32,0.12])translate([0,0,z-5.5])anel(97.25,102.75,11);}
  for(a=[45:90:315])translate([raio_furos*cos(a),raio_furos*sin(a),0]){
    color([0.85,0.89,0.82]){
      translate([0,0,8])espacador(h_esp_inf);
      translate([0,0,centro_z[0]+h_bobina/2])espacador(h_esp_meio);
      translate([0,0,-5])cylinder(h=180,d=3);
      for(z=[-0.5,centro_z[1]+h_bobina/2])translate([0,0,z])anel(1.7,3,0.5);
      for(z=[-2.9,centro_z[1]+h_bobina/2+0.5])translate([0,0,z])difference(){cylinder(h=2.4,r=5.5/sqrt(3),$fn=6);translate([0,0,-0.1])cylinder(h=2.6,d=3);}
    }
  }
  for(x=[-110,110],y=[-110,110])color([0.08,0.09,0.11])translate([x,y,-6])cylinder(h=6,d=12);
}
if(modo=="montagem")montagem();
if(modo=="bobina")bobina();
if(modo=="base")base();
if(modo=="espacador_inferior")espacador(h_esp_inf);
if(modo=="espacador_meio")espacador(h_esp_meio);
