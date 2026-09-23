import argparse, json, os
from .data_loader import Dataset
from .pipeline import ProductTruthPipeline

TARGETS=['MODULE','GLOBAL_INTERSPACE_CLAIM','GLOBAL_CONSUMER_LIFESTAGE_CLAIM','GLOBAL_PACKAGING','GLOBAL_IF_MEDICATED','GLOBAL_PERCENTAGE_NATURAL_INGREDIENTS','GLOBAL_IF_WITH_SENSITIVE_CLAIM','GLOBAL_ORAL_CARE_FUNCTION','GLOBAL_IF_WITH_FLUORIDE','GLOBAL_FLAVOUR_FRAGRANCE_INGREDIENT_GROUP','GLOBAL_METHOD_OF_APPLICATION_DISPENSE','GLOBAL_PACKAGING_MATERIAL','GLOBAL_DESCRIPTIVE_SIZE_OF_TOOTHBRUSH_HEAD_CLAIM','GLOBAL_BRISTLE_STRENGTH_CLAIM','GLOBAL_FLAVOUR_FRAGRANCE_INGREDIENT']

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--limit',type=int,default=5); ap.add_argument('--start',type=int,default=0); ap.add_argument('--out',default='outputs/dev_results.jsonl'); args=ap.parse_args()
    ds=Dataset(); pipe=ProductTruthPipeline(); os.makedirs(os.path.dirname(args.out) or '.',exist_ok=True)
    with open(args.out,'w',encoding='utf8') as f:
        for i in range(args.start,min(args.start+args.limit,len(ds.dev))):
            row=ds.dev.iloc[i]
            try:
                pred,cands=pipe.run(row,web=True)
                truth=row.to_dict(); correct={k: (str(pred.get('module','')).strip().upper()==str(truth.get('MODULE','')).strip().upper()) if k=='MODULE' else (str(pred.get('characteristics',{}).get(k,'')).strip().upper()==str(truth.get(k,'')).strip().upper()) for k in TARGETS if str(truth.get(k,''))!=''}
                score=sum(correct.values())/len(correct) if correct else 0
                obj={'row':i,'score':score,'correct':correct,'prediction':pred,'candidates':cands}
            except Exception as e: obj={'row':i,'error':str(e)}
            f.write(json.dumps(obj,ensure_ascii=False,default=str)+'\n'); print(f'[{i+1}/{min(args.start+args.limit,len(ds.dev))}] {obj.get("score", "ERROR")}')

if __name__=='__main__': main()
