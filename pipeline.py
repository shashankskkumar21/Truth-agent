from .data_loader import Dataset
from .retrieval import retrieve_product
from .luna_agent import LunaAgent
from .validator import validate, missing_characteristics

class ProductTruthPipeline:
    def __init__(self,dataset_path=None):
        self.ds=Dataset(dataset_path) if dataset_path else Dataset()
        self.luna=LunaAgent()

    def run(self,row,web=True):
        row=dict(row)
        candidates=retrieve_product(row) if web else []
        selection=self.luna.select_product(row,candidates)
        chosen_url=selection.get('product_url') or selection.get('url')
        if chosen_url:
            chosen=[c for c in candidates if c.get('url')==chosen_url]
            if chosen: evidence=chosen[0:1]
            else: evidence=candidates[:1]
        else:
            evidence=candidates[:4]
        module=str(row.get('MODULE','')).strip()
        if not module:
            mod=self.luna.classify_module(row,self.ds.modules,evidence)
            module=str(mod.get('module','')).strip()
            module_conf=mod.get('confidence','low')
            module_reason=mod.get('reasoning','')
        else:
            module_conf='ground_truth_input'; module_reason='Module supplied by development dataset.'
        if module not in self.ds.modules:
            raise ValueError(f'Luna selected a module not present in taxonomy: {module!r}')
        context=self.ds.context(module)
        ev=[]
        for c in evidence[:4]:
            p=c.get('page',{})
            ev.append({'title':c.get('title'),'url':c.get('url'),'snippet':c.get('snippet'),'score':c.get('score'),'page_text':p.get('text','')})
        pred=self.luna.classify_characteristics(row,context,ev,chosen_url or '')
        clean,errors=validate(pred,context)
        missing=missing_characteristics({'characteristics':clean},context)
        result={
            'ITEM_CODE':row.get('ITEM_CODE',''),'EXTERNAL_CODE':row.get('EXTERNAL_CODE',''),'BRAND':row.get('BRAND',''),'RETAILER_DESC':row.get('RETAILER_DESC',''),
            'product_url':chosen_url or '', 'module':module, 'module_confidence':module_conf,
            'module_reasoning':module_reason, 'selection':selection, 'characteristics':clean,
            'reasoning':pred.get('reasoning',''),'evidence':pred.get('evidence',[]),'validation_errors':errors,'missing_characteristics':missing,
        }
        return result,candidates
