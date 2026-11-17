import os
import math
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
 'repeat_animal_products':('Animal products','Loss','losses_animalsp','animal_production'),
}

# Survey field: property_group/parish (XLSForm V2.1). Carriacou and Petite
# Martinique are one administrative dependency, not a seventh parish.
PARISH_LABELS = {
 'saint_andrew': 'Saint Andrew',
 'saint_david': 'Saint David',
 'saint_george': 'Saint George',
 'saint_john': 'Saint John',
 'saint_mark': 'Saint Mark',
 'saint_patrick': 'Saint Patrick',
 'carriacou_petite_martinique': 'Carriacou and Petite Martinique',
}
NOT_ASSIGNED = 'Not assigned (older records)'
PARISH_ORDER = list(PARISH_LABELS.values()) + [NOT_ASSIGNED]

# Original choice labels from the deployed MULTICROP XLSForm.
PRODUCT_LABELS = {'animal': {'beef': 'Beef',
            'dairy': 'Dairy',
            'goat': 'Goat',
            'pig': 'Pig',
            'poultry broiler': 'Poultry broilers',
            'poultry layer': 'Poultry layers',
            'sheep': 'Sheep'},
 'animal_production': {'eggs': 'Eggs per unit', 'milk': 'Milk in liters'},
 'forestrees1': {'almond': 'Almond',
                 'bagul': 'Bagul',
                 'bamboo': 'Bamboo',
                 'bluemahoe': 'Blue Mahoe',
                 'builet': 'Builet',
                 'cacolay': 'Cacolay',
                 'calabash': 'Calabash',
                 'cassiaforest': 'Cassia Forest',
                 'christmastrees': 'Christmas Trees',
                 'cutlet': 'Cutlet',
                 'eucalytus': 'Eucalytus',
                 'gaiba': 'Gaiba',
                 'gliricidia': 'Gliricidia',
                 'gommier': 'Gommier',
                 'hogplum': 'Hog Plum',
                 'leucaena': 'Leucaena',
                 'lowland': 'Lowland',
                 'mahogany': 'Mahogany',
                 'mangrove': 'Mangrove',
                 'maruba': 'Maruba',
                 'pennypiece': 'Penny Piede',
                 'pine ': 'Pine ',
                 'poisdoux': 'Poisdoux',
                 'redcedar': 'red cedar',
                 'saman': 'Saman',
                 'sandbox': 'Sandbox',
                 'slikcottom': 'Slikcotton',
                 'tantakayo': 'Tantakayo',
                 'tapana': 'Tapana',
                 'teak': 'Teak',
                 'whitecedar': 'White Cedar'},
 'forestrees2': {'almondbd': 'Almond (bd.ft)',
                 'bagulbd': 'Bagul (bd.ft)',
                 'bamboobd': 'Bamboo (bd.ft)',
                 'bluemahoebd': 'Blue Mahoe  (bd.ft)',
                 'builetbd': 'Builet  (bd.ft)',
                 'cacolaybd': 'Cacolay (bd.ft)',
                 'calabashbd': 'Calabash (bd.ft)',
                 'cassiaforestbd': 'Cassia Forest (bd.ft)',
                 'christmastreesbd': 'Christmas Trees  (bd.ft)',
                 'cutletbd': 'Cutlet (bd.ft)',
                 'eucalytusbd': 'Eucalytus (bd.ft)',
                 'gaibabd': 'Gaiba  (bd.ft)',
                 'gliricidiabd': 'Gliricidia (bd.ft)',
                 'gommierbd': 'Gommier  (bd.ft)',
                 'hogplumbd': 'Hog Plum (bd.ft)',
                 'leucaenabd': 'Leucaena (bd.ft)',
                 'lowlandbd': 'Lowland (bd.ft)',
                 'mahoganybd': 'Mahogany (bd.ft)',
                 'mangrovebd': 'Mangrove (bd.ft)',
                 'marubabd': 'Maruba  (bd.ft)',
                 'pennypiecebd': 'Penny Piede (bd.ft)',
                 'pinebd': 'Pine  (bd.ft)',
                 'poisdouxbd': 'Poisdoux  (bd.ft)',
                 'redcedarbd': 'Red Cedar (bd.ft)',
                 'samanbd': 'Saman (bd.ft)',
                 'sandboxbd': 'Sandbox (bd.ft)',
                 'slikcottombd': 'Slikcotton (bd.ft)',
                 'tantakayobd': 'Tantakayo (bd.ft)',
                 'tapanabd': 'Tapana  (bd.ft)',
                 'teakbd': 'Teak (bd.ft)',
                 'whitecedarbd': 'White Cedar (bd.ft)'},
 'product': {'ackee': 'Ackee ',
             'atemoya': 'Atemoya',
             'avocado': 'Avocado',
             'banana': 'Banana',
             'breadfruit': 'Breadfruit ',
             'breadnut': 'Breadnut',
             'cashewnut': 'Cashew Nut',
             'chenip': 'Chenip',
             'cocoa': 'Cocoa',
             'coconut': 'Coconut',
             'coffee': 'Coffee',
             'condicion': 'Condicion',
             'custardapple': 'Custard Apple',
             'damson': 'Damson',
             'frenchcashew': 'French Cashew',
             'goldenapple': 'Golden Apple',
             'governorplum': 'Governor Plum',
             'grapevines': 'Grape (vines)',
             'guava': 'Guava',
             'mammieapple': 'Mammie Apple',
             'mangografted': 'Mango (Grafted)',
             'mangoseedling': 'Mango (seedling)',
             'mauby': 'Mauby',
             'nutmegmarcott': 'Nutmeg/marcott',
             'nutmegseedling': 'Nutmeg/Seedling',
             'passionf': 'Passion Fruit',
             'pawpaw': 'Pawpaw (Table)',
             'plum ': 'Plum (Red & Yellow)',
             'sapodilla': 'Sapodilla',
             'starapple': 'Star Apple',
             'sugarapple': 'Sugar Apple',
             'tamarind': 'Tamarind',
             'westcherry': 'West Indian Cherry'},
 'productc': {'banana': 'Banana',
              'bayleaf': 'Bay Leaf',
              'bluggoes': 'bluggoes',
              'cinnamon': 'Cinnamon',
              'citrus ': 'Citrus ',
              'cloves': 'Cloves',
              'greendie': 'Greendie',
              'grosmichel': 'Gros Michel',
              'mountainspice': 'Mountain Spice',
              'pelipita': 'Pelipita',
              'pimento': 'Pimento',
              'plantain ': 'Plantain ',
              'rockfig': 'Rock Fig',
              'sapot': 'Sapot',
              'tonkabean': 'Tonka Bean'},
 'productd': {'blacktulip': 'Black Tulip',
              'cassia': 'Cassia',
              'casurina': 'Casurina',
              'collisina': 'H. Collisina',
              'costos': 'Costos',
              'flamboyant': 'Flamboyant',
              'flamered': 'H. Flame Red',
              'goldenopal': 'H. Golden Opal',
              'goldentorch': 'H. Golden Torch',
              'heliconiacaribea': 'Heliconia Caribea',
              'immortell': 'Immortell',
              'musacoccina': 'Musa Coccina',
              'musaonatto': 'Musa Onatto',
              'musaveluctina': 'Musa Veluctina',
              'perfumeginger': 'Perfume Ginger',
              'pineappleginger': 'Pineapple Ginger',
              'pinkginger': 'Pink Ginger Lily',
              'renginger': 'Red Ginger Lily',
              'richmondred': 'H. Richmond Red',
              'rostrata': 'H. Rostrata',
              'sexypink': 'H. Sexy Pink',
              'shampooginger': 'Shampoo Ginger',
              'torchlily': 'Torch Lily',
              'wagneriana': 'H. Wagneriana',
              'wildtamarind': 'Wild Tamarind'},
 'producte': {'ackee': 'Ackee',
              'atemoya': 'Atemoya',
              'avocado': 'Avocado',
              'banana': 'Banana',
              'breadfruit': 'Breadfruit',
              'breadnut': 'Breadnut',
              'cashewnut': 'Cashew Nut',
              'chenip': 'Chenip',
              'cocoa': 'Cocoa',
              'coconut ': 'Coconut',
              'coffee': 'Coffee',
              'condicion': 'Condicion',
              'custardapple': 'Custard Apple',
              'damson': 'Damson',
              'frenchcashew': 'French Cashew',
              'goldenapple': 'Golden Apple',
              'governorplum': 'Governor Plum',
              'grapevines': 'Grape (vines)',
              'guava': 'Guava',
              'mammieapple': 'Mammie Apple',
              'mangografted': 'Mango (Grafted)',
              'mangoseedling': 'Mango (seedling)',
              'mauby': 'Mauby',
              'passionf': 'Passion Fruit',
              'pawpaw': 'Pawpaw (Table)',
              'plum ': 'Plum (Red & Yellow)',
              'sapodilla': 'Sapodilla',
              'starapple': 'Star Apple',
              'sugarapple': 'Sugar Apple',
              'tamarind': 'Tamarind',
              'westcherry': 'West Indian Cherry'},
 'productf': {'banana': 'Banana',
              'bayleaf': 'Bay Leaf',
              'bluggoes': 'bluggoes',
              'cinnamon': 'Cinnamon',
              'citrus': 'Citrus',
              'cloves': 'Cloves',
              'greendie': 'Greendie',
              'grosmichel': 'Gros Michel',
              'mountainspice': 'Mountain Spice',
              'pelipita': 'Pelipita',
              'pimento': 'Pimento',
              'plantain ': 'Plantain ',
              'rockfig': 'Rock Fig',
              'sapot': 'Sapot',
              'tonkabean': 'Tonka Bean'},
 'productg': {'blacktulip': 'Black Tulip',
              'cassia': 'Cassia',
              'casurina': 'Casurina',
              'collisina': 'H. Collisina',
              'costos': 'Costos',
              'flamboyant': 'Flamboyant',
              'flamered': 'H. Flame Red',
              'goldenopal': 'H. Golden Opal',
              'goldentorch': 'H. Golden Torch',
              'heliconiacaribea': 'Heliconia Caribea',
              'inmotell': 'Inmotell',
              'musacoccina': 'Musa Coccina',
              'musaonatto': 'Musa Onatto',
              'musaveluctina': 'Musa Veluctina',
              'perfumeginger': 'Perfume Ginger',
              'pineappleginger': 'Pineapple Ginger',
              'pinkginger': 'Pink Ginger Lily',
              'renginger': 'Red Ginger Lily',
              'richmondred': 'H. Richmond Red',
              'rostrata': 'H. Rostrata',
              'sexypink': 'H. Sexy Pink',
              'shampooginger': 'Shampoo Ginger',
              'torchlily': 'Torch Lily',
              'wagneriana': 'H. Wagneriana',
              'wildtamarind': 'Wild Tamarind'},
 'producth': {'beans': 'Beans (Bush type)',
              'beet': 'Beet',
              'broccoli': 'Broccoli',
              'butternutsquash': 'Butternut Squash',
              'cabbage': 'Cabbage',
              'cantaloupe': 'Cantaloupe',
              'carrot': 'Carrot',
              'cassava': 'Cassava',
              'cauliflower': 'Cauliflower',
              'celery': 'Celery',
              'chives': 'Chives',
              'cornandpeas': 'Corn and Peas together',
              'cornstool': 'Corn Stool (Solid Stand)',
              'cucumber': 'Cucumber',
              'cutyam': 'Cut Yam (Bush Yam)',
              'dasheen': 'Dasheen (Holes)',
              'eddoes': 'Eddoes (Holes)',
              'eggplant': 'Egg Plant',
              'ginger': 'Ginger',
              'groundnut': 'Ground Nut',
              'hotpepper': 'Hotpepper',
              'lettuce': 'Lettuce',
              'melonfruit': 'Melon (fruit)',
              'melonvine': 'Melon (vine)',
              'okra': 'Okra',
              'onion': 'Onion',
              'parsley': 'Parsley',
              'peasstool': 'Peas Stool (Solid Stand)',
              'pumpkinfruit': 'Pumpkin (fruit)',
              'pumpkinvine': 'Pumpkin (Vine)',
              'sorrel': 'Sorrel',
              'stringbeans': 'String Beans',
              'sugarcane': 'Sugar Cane per Square Foot',
              'sweetpepper': 'Sweet Pepper',
              'sweetpotatoes': 'Sweet Potatoes (Holes)',
              'tannias': 'Tannias (Holes)',
              'thyme': 'Thyme',
              'tomatoes': 'tomatoes',
              'watercress': 'Water Cress (Sq. Ft.)',
              'yarn': 'Yarn (Lisbon etc)'},
 'producti': {'beansin': 'Beans (Bush type)',
              'beetin': 'Beet',
              'broccoliin': 'Broccoli',
              'butternutsquashin': 'Butternut Squash',
              'cabbagein': 'Cabbage',
              'cantaloupein': 'Cantaloupe',
              'carrotin': 'Carrot',
              'cassavain': 'Cassava',
              'cauliflowerin': 'Cauliflower',
              'celeryin': 'Celery',
              'chivesin': 'Chives',
              'cornandpeasin': 'Corn and Peas together',
              'cornstoolin': 'Corn Stool (Solid Stand)',
              'cucumberin': 'Cucumber',
              'cutyamin': 'Cut Yam (Bush Yam)',
              'dasheenin': 'Dasheen (Holes)',
              'eddoesin': 'Eddoes (Holes)',
              'eggplantin': 'Egg Plant',
              'gingerin': 'Ginger',
              'groundnutin': 'Ground Nut',
              'hotpepperin': 'Hotpepper',
              'lettucein': 'Lettuce',
              'melonfruitin': 'Melon (fruit)',
              'melonvinein': 'Melon (vine)',
              'okrain': 'Okra',
              'onionin': 'Onion',
              'parsleyin': 'Parsley',
              'peasstoolin': 'Peas Stool (Solid Stand)',
              'pumpkinfruitin': 'Pumpkin (fruit)',
              'pumpkinvinein': 'Pumpkin (Vine) ',
              'sorrelin': 'Sorrel',
              'stringbeansin': 'String Beans',
              'sugarcanein': 'Sugar Cane per Square Foot',
              'sweetpepperin': 'Sweet Pepper',
              'sweetpotatoesin': 'Sweet Potatoes (Holes)',
              'tanniasin': 'Tannias (Holes)',
              'thymein': 'Thyme',
              'tomatoesin': 'tomatoes',
              'watercressin': 'Water Cress (Sq. Ft.)',
              'yarnin': 'Yarn (Lisbon etc)'}}

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

def leaf(d, name):
    """Find a scalar field even when Kobo adds group/repeat prefixes."""
    if not isinstance(d, dict):
        return None
    if name in d and not isinstance(d[name], (dict, list)):
        return d[name]
    for key, value in d.items():
        if str(key).split('/')[-1] == name and not isinstance(value, (dict, list)):
            return value
    for value in d.values():
        if isinstance(value, dict):
            found = leaf(value, name)
            if found is not None:
                return found
    return None


def get_repeat(d, name):
    """Handle nested and slash-prefixed Kobo repeat arrays."""
    if isinstance(d, list):
        for child in d:
            found = get_repeat(child, name)
            if found:
                return found
        return []
    if not isinstance(d, dict):
        return []
    for key, value in d.items():
        if str(key).split('/')[-1] == name and isinstance(value, list):
            return value
    for value in d.values():
        if isinstance(value, (dict, list)):
            found = get_repeat(value, name)
            if found:
                return found
    return []


def product_label(field, raw):
    if raw is None or str(raw).strip().lower() in ('', 'none', 'nan', 'null'):
        return None
    code = str(raw).strip()
    return PRODUCT_LABELS.get(field, {}).get(code, code.replace('_', ' ').capitalize())

def number(v):
 try:
  converted=float(v or 0)
  return converted if math.isfinite(converted) else 0.0
 except (ValueError,TypeError):return 0.0

def parish_label(raw):
 if raw is None or str(raw).strip().lower() in ('', 'nan', 'none', 'null'):
  return NOT_ASSIGNED
 key=str(raw).strip().lower().replace(' ', '_').replace('&', 'and')
 aliases={'st_andrew':'saint_andrew','st_david':'saint_david',
          'st_george':'saint_george','st_john':'saint_john',
          'st_mark':'saint_mark','st_patrick':'saint_patrick',
          'carriacou_and_petite_martinique':'carriacou_petite_martinique'}
 key=aliases.get(key,key)
 return PARISH_LABELS.get(key,str(raw).strip())

def fmt(v):return f'EC$ {v:,.2f}'

def parse(records):
 farms=[];items=[]
 for rec in records:
  rid=str(rec.get('_id',rec.get('__id','')))
  damage=number(leaf(rec,'summary_damage'));loss=number(leaf(rec,'summary_losses'));impact=number(leaf(rec,'summary_impact'))
  parish=parish_label(leaf(rec,'parish'))
  gps=leaf(rec,'location_gps')
  lat=lon=None
  try:
   if isinstance(gps,str):lat,lon=map(float,gps.split()[:2])
   elif isinstance(gps,dict):lat=float(gps['latitude']);lon=float(gps['longitude'])
  except (ValueError,TypeError,KeyError):pass
  farms.append({'id':rid,'Farm':str(leaf(rec,'farm_code') or leaf(rec,'Property') or rid),'Parish':parish,'Date':str(leaf(rec,'assessment_date') or rec.get('_submission_time',''))[:10],'Damage':damage,'Losses':loss,'Impact':impact,'latitude':lat,'longitude':lon})
  for key,(group,effect,amount,product) in REPEATS.items():
    for entry in get_repeat(rec,key):
     if not isinstance(entry,dict):continue
     val=number(leaf(entry,amount))
     pname=leaf(entry,product)
     if pname is None:
      for k,v in entry.items():
       if str(k).split('/')[-1].lower().startswith(('product','animal','forestrees')) and isinstance(v,(str,int)):
        pname=v;break
     label=product_label(product,pname)
     # Empty optional repeats are not real product observations.
     if label is None and abs(val)<0.000001:continue
     items.append({'Assessment ID':rid,'Parish':parish,'Group':group,'Effect':effect,
                   'Product':label or 'Unspecified product','Amount':val})
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

# The filter is applied both to assessment-level amounts and to repeat rows.
# Earlier submissions cannot be assigned to a parish from missing Kobo data.
with st.sidebar:
 st.header('Parish / administrative area')
 available=[p for p in PARISH_ORDER if p in set(farms['Parish'])]
 available += sorted(set(farms['Parish'])-set(available))
 selected=st.multiselect('Show areas',options=available,default=available)
 st.caption('Records collected before the parish question appear as Not assigned.')
farms=farms[farms['Parish'].isin(selected)].copy()
if not items.empty:
 items=items[items['Parish'].isin(selected)].copy()
if farms.empty:
 st.info('No assessments match the selected parish filter. Select at least one area in the sidebar.')
 st.stop()

c1,c2,c3,c4=st.columns(4)
c1.metric('Agricultural assessments',f'{len(farms):,}')
c2.metric('Total damage',fmt(farms.Damage.sum()))
c3.metric('Total losses',fmt(farms.Losses.sum()))
c4.metric('Total impact',fmt(farms.Impact.sum()))
st.caption(f'Average damage per assessment: {fmt(farms.Damage.mean())}. Each assessment is counted once in these totals.')
if abs(farms.Impact.sum()-farms.Damage.sum()-farms.Losses.sum())>0.02:
 st.warning('Some records have Total Impact different from Damage + Losses. Review Kobo calculations.')

st.subheader('Damage and losses by parish / administrative area')
parish_totals=(farms.groupby('Parish',as_index=False)
               .agg(Assessments=('id','size'),Damage=('Damage','sum'),
                    Losses=('Losses','sum'),Impact=('Impact','sum')))
parish_totals['_order']=parish_totals['Parish'].map(
                          {name:i for i,name in enumerate(PARISH_ORDER)}).fillna(len(PARISH_ORDER))
parish_totals=(parish_totals.sort_values(['_order','Parish'])
               .drop(columns=['_order']).reset_index(drop=True))
parish_long=parish_totals.melt(id_vars=['Parish'],value_vars=['Damage','Losses'],
                               var_name='Effect',value_name='EC$')
fig=px.bar(parish_long,x='Parish',y='EC$',color='Effect',barmode='stack',
           category_orders={'Parish':parish_totals['Parish'].tolist()},
           hover_data={'EC$':':,.2f'})
fig.update_layout(xaxis_title='',yaxis_title='EC$',legend_title_text='')
st.plotly_chart(fig,use_container_width=True)
with st.expander('Parish summary — values in EC$',expanded=True):
 st.dataframe(parish_totals,hide_index=True,use_container_width=True,
              column_config={
               'Damage':st.column_config.NumberColumn('Damage (EC$)',format='%.2f'),
               'Losses':st.column_config.NumberColumn('Losses (EC$)',format='%.2f'),
               'Impact':st.column_config.NumberColumn('Impact (EC$)',format='%.2f')})
 st.download_button('Download parish summary (CSV)',
                    parish_totals.to_csv(index=False).encode('utf-8-sig'),
                    'agriculture_parish_summary.csv','text/csv')

if not items.empty:
 st.subheader('Analysis by agricultural group and product')
 effect=st.selectbox('Type of effect',['All','Damage','Loss'])
 view=items if effect=='All' else items[items.Effect==effect]
 a,b=st.columns(2)
 with a:
  grouped=view.groupby(['Group','Effect'],as_index=False).Amount.sum()
  st.plotly_chart(px.bar(grouped,x='Amount',y='Group',color='Effect',orientation='h',labels={'Amount':'EC$'}),use_container_width=True)
 with b:
  st.markdown('**Damage and losses by product**')
  product_rows = view.copy()
  product_rows['Product'] = product_rows['Product'].fillna('').astype(str).str.strip()
  product_rows['Amount'] = pd.to_numeric(product_rows['Amount'], errors='coerce').fillna(0)
  product_rows = product_rows[(product_rows['Product'] != '') & (product_rows['Amount'].abs() > 0.000001)]
  if product_rows.empty:
   st.warning('No product-level amounts are available in the API response. Check the repeat records below.')
  else:
   product_totals = (product_rows.groupby(['Product','Effect'], as_index=False)['Amount']
                     .sum().sort_values('Amount', ascending=False).head(25))
   # Horizontal bars avoid the empty category-axis issue seen with the original vertical plot.
   fig = px.bar(product_totals, x='Amount', y='Product', color='Effect',
                orientation='h', barmode='group', labels={'Amount':'EC$'},
                hover_data={'Amount':':,.2f'})
   fig.update_layout(yaxis={'type':'category','categoryorder':'total ascending'},
                     xaxis={'rangemode':'tozero'}, height=max(350, 34*len(product_totals)+100))
   st.plotly_chart(fig, use_container_width=True)
   with st.expander('Product totals — verification table'):
    st.dataframe(product_totals.rename(columns={'Amount':'EC$'}),hide_index=True,use_container_width=True)
 with st.expander('Diagnostic: repeat records and product names'):
  st.caption('If a product name is missing, this table helps identify which repeat group requires an API field mapping correction. No credentials are displayed.')
  st.dataframe(view[['Assessment ID','Group','Effect','Product','Amount']],hide_index=True,use_container_width=True)
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
st.caption('PDNA Agriculture Dashboard V2.1 · Grenada · KoboToolbox API')
