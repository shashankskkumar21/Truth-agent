import json
import pandas as pd
from .data_loader import Dataset, OUTPUT_COLUMNS

def result_to_row(result, base=None):
    row=dict(base or {})
    row['PRODUCT_URL']=result.get('product_url','')
    row['REASONING']=result.get('reasoning','')
    row['MODULE']=result.get('module','')
    for k,v in result.get('characteristics',{}).items(): row[k]=v
    return {c:row.get(c,'') for c in OUTPUT_COLUMNS}

def export_results(results, out='outputs/predictions.xlsx', bases=None):
    ds=Dataset(); rows=[]
    for i,r in enumerate(results):
        base=(bases[i] if bases else {})
        rows.append(result_to_row(r,base))
    pd.DataFrame(rows,columns=OUTPUT_COLUMNS).to_excel(out,index=False)
    return out
