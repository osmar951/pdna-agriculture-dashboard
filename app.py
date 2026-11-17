import os
import requests
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title='PDNA Agriculture | Grenada',page_icon='🌱',layout='wide')
st.title('🌱 PDNA Agriculture — Grenada')
st.caption('Agricultural Damage and Loss Assessment · Currency: EC$ (XCD) · Live KoboToolbox data')
UID='asrBXTfAXfnqdMn9q4pdK5'
REPEATS={
 'repeat_immature_trees':('Immature trees','Damage','direct_damage','product'),
 'repeat_spices_tree':('Spices, citrus & banana (trees)','Damage','direct_damagec','productc'),
 'repeat_ornamentals_immature':('Immature ornamentals','Damage','direct_damaged','productd'),
 'repeat_forest_immature':('Immature forest trees','Damage','direct_damageft','forestrees1'),
 'repeat_animal_damage':('Animals','Damage','damage_animalssum','animal'),
 'repeat_fruit_bearing':('Fruit (bearing)','Loss','direct_lossesa','producte'),
 'repeat_spices_bearing':('Spices, citrus & banana (bearing)','Loss','direct_lossesb','productf'),
 'repeat_ornamentals_bearing':('Ornamentals (bearing)','Loss','direct_lossesc','productg'),
 'repeat_vines_bearing':('Vines, roots, legumes & vegetables (bearing)','Loss','direct_lossesd','producth'),
 'repeat_vines_immature':('Vines, roots, legumes & vegetables (immature)','Loss','direct_lossese','producti'),
 'repeat_forest_mature':('Mature forest trees','Loss','direct_lossesft2','forestrees2'),
 'repeat_animal_products':('Animal products','Loss','losses_animalsp','animalp'),
}

def cfg(k,default=''):
 try:return st.secrets.get(k,os.environ.get(k,default))
 except Exception:return os.environ.get(k,default)

@st.cache_data(ttl=300,show_spinner='Loading KoboToolbox assessments…')
def load_data(server,uid,token):
 base=server.rstrip('/')+'/api/v2/assets/'+uid+'/data/'
 headers={'Authorization':'Token '+token}
 url=base+'?format=json&page_size=1000'
 records=[]
 while url:
  r=requests.get(url,headers=headers,timeout=40);r.raise_for_status()
  obj=r.json()
  if isinstance(obj,list):records+=obj;break
  records+=obj.get('results',[])
  url=obj.get('next')
 return records

def leaf(d,name):
 if not isinstance(d,dict):return None
 if name in d:return d[name]
 for k,v in d.items():
  if k.split('/')[-1]==name and not isinstance(v,(list,dict)):return v
 return None

def get_repeat(d,name):
 if name in d and isinstance(d[name],list):return d[name]
 for k,v in d.items():
  if k.split('/')[-1]==name and isinstance(v,list):return v
  if isinstance(v,dict):
   result=get_repeat(v,name)
   if result:return result
 return []

def number(v):
 try:return float(v or 0)
 except (ValueError,TypeError):return 0.0

def fmt(v):return f'EC$ {v:,.2f}'

def parse(records):
 farms=[];items=[]
 for rec in records:
  rid=str(rec.get('_id',rec.get('__id','')))
  damage=number(leaf(rec,'summary_damage'));loss=number(leaf(rec,'summary_losses'));impact=number(leaf(rec,'summary_impact'))
  gps=leaf(rec,'location_gps')
  lat=lon=None
  try:
   if isinstance(gps,str):lat,lon=map(float,gps.split()[:2])
   elif isinstance(gps,dict):lat=float(gps['latitude']);lon=float(gps['longitude'])
  except (ValueError,TypeError,KeyError):pass
  farms.append({'id':rid,'Farm':str(leaf(rec,'farm_code') or leaf(rec,'Property') or rid),'Date':str(leaf(rec,'assessment_date') or rec.get('_submission_time',''))[:10],'Damage':damage,'Losses':loss,'Impact':impact,'latitude':lat,'longitude':lon})
  for key,(group,effect,amount,product) in REPEATS.items():
   for entry in get_repeat(rec,key):
    if not isinstance(entry,dict):continue
    val=number(leaf(entry,amount))
    pname=leaf(entry,product)
    if pname is None:
     for k,v in entry.items():
      if k.lower().startswith(('product','animal','forestrees')) and isinstance(v,(str,int)):pname=v;break
    items.append({'Assessment ID':rid,'Group':group,'Effect':effect,'Product':str(pname or 'Unspecified'),'Amount':val})
 return pd.DataFrame(farms),pd.DataFrame(items)

with st.sidebar:
 st.header('Data source')
 server=cfg('KOBO_SERVER','https://kf.kobotoolbox.org')
 uid=cfg('KOBO_ASSET_UID',UID)
 token=cfg('KOBO_API_TOKEN')
 st.write('Kobo asset:',uid)
 if st.button('🔄 Refresh Kobo data'):
  load_data.clear();st.rerun()
 st.caption('Refresh automatically every 5 minutes. Keep the API token in Streamlit Secrets, not GitHub.')

if not token:
 st.warning('Add KOBO_API_TOKEN in Streamlit → App settings → Secrets. See README.md for instructions.')
 st.stop()
try: records=load_data(server,uid,token)
except Exception as exc:
 st.error(f'Unable to retrieve Kobo data: {exc}');st.stop()
farms,items=parse(records)
if farms.empty:st.info('No Kobo submissions found yet.');st.stop()

c1,c2,c3,c4=st.columns(4)
c1.metric('Agricultural assessments',f'{len(farms):,}')
c2.metric('Total damage',fmt(farms.Damage.sum()))
c3.metric('Total losses',fmt(farms.Losses.sum()))
c4.metric('Total impact',fmt(farms.Impact.sum()))
st.caption(f'Average damage per assessment: {fmt(farms.Damage.mean())}. Each assessment is counted once in these totals.')
if abs(farms.Impact.sum()-farms.Damage.sum()-farms.Losses.sum())>0.02:
 st.warning('Some records have Total Impact different from Damage + Losses. Review Kobo calculations.')

st.subheader('Damage and losses by assessment')
long=farms.melt(id_vars=['Farm','id'],value_vars=['Damage','Losses'],var_name='Effect',value_name='EC$')
st.plotly_chart(px.bar(long,x='Farm',y='EC$',color='Effect',barmode='stack',hover_data=['id']),use_container_width=True)

if not items.empty:
 st.subheader('Analysis by agricultural group and product')
 effect=st.selectbox('Type of effect',['All','Damage','Loss'])
 view=items if effect=='All' else items[items.Effect==effect]
 a,b=st.columns(2)
 with a:
  grouped=view.groupby(['Group','Effect'],as_index=False).Amount.sum()
  st.plotly_chart(px.bar(grouped,x='Amount',y='Group',color='Effect',orientation='h',labels={'Amount':'EC$'}),use_container_width=True)
 with b:
  grouped=view.groupby(['Product','Effect'],as_index=False).Amount.sum().sort_values('Amount',ascending=False).head(20)
  st.plotly_chart(px.bar(grouped,x='Product',y='Amount',color='Effect',labels={'Amount':'EC$'}),use_container_width=True)
 st.caption('Product-level figures are derived from Kobo repeat groups; assessment-level totals come only from parent submissions. Product subtotals may not include all additional costs or categories.')
 st.download_button('Download product details (CSV)',view.to_csv(index=False).encode('utf-8-sig'),'agriculture_products.csv','text/csv')
else:st.info('No repeated product records found. Verify that repeat groups are present in the Kobo API response.')

st.subheader('Geographic distribution')
points=farms.dropna(subset=['latitude','longitude'])
points=points[points.latitude.between(-90,90)&points.longitude.between(-180,180)]
if len(points):
 st.map(points,latitude='latitude',longitude='longitude',size=100)
 st.caption('GPS coordinates reflect submitted data. Test submissions may be located outside Grenada.')
else:st.info('No valid GPS coordinates in current submissions.')

st.subheader('Assessment records')
st.dataframe(farms.drop(columns=['latitude','longitude']),use_container_width=True,hide_index=True)
st.download_button('Download assessments (CSV)',farms.to_csv(index=False).encode('utf-8-sig'),'agriculture_assessments.csv','text/csv')
st.caption('PDNA Agriculture Dashboard V1 · Grenada · KoboToolbox API')
