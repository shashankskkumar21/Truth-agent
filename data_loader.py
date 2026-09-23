from pathlib import Path
import ast
import pandas as pd

DEFAULT_DATASET = Path(__file__).resolve().parents[1] / 'data' / 'product_truth_agent_dataset.xlsx'
OUTPUT_COLUMNS = list(pd.read_excel(DEFAULT_DATASET, sheet_name='sample_output', nrows=0).columns)
CHAR_COLUMNS = [c for c in OUTPUT_COLUMNS if c.startswith('GLOBAL_')]

class Dataset:
    def __init__(self, path=DEFAULT_DATASET):
        self.path = Path(path)
        self.dev = pd.read_excel(self.path, sheet_name='dev').fillna('')
        self.qa = pd.read_excel(self.path, sheet_name='qa').fillna('')
        self.values = pd.read_excel(self.path, sheet_name='char_value_list').fillna('')
        self.guidelines = pd.read_excel(self.path, sheet_name='char_guidelines').fillna('')
        self.sample = pd.read_excel(self.path, sheet_name='sample_output').fillna('')
        self.guide = pd.read_excel(self.path, sheet_name='dataset_understanding_guide').fillna('')

    @staticmethod
    def parse_values(value):
        if isinstance(value, (list, tuple)):
            return [str(x).strip() for x in value]
        s = str(value).strip()
        if not s:
            return []
        try:
            parsed = ast.literal_eval(s)
            if isinstance(parsed, (list, tuple)):
                return [str(x).strip() for x in parsed]
        except Exception:
            pass
        return [x.strip() for x in s.split('|') if x.strip()]

    @staticmethod
    def norm(value):
        return ' '.join(str(value or '').strip().upper().split())

    @property
    def modules(self):
        return sorted({str(x).strip() for x in self.values['module'] if str(x).strip()})

    def taxonomy_for_module(self, module):
        m = self.norm(module)
        rows = self.values[self.values['module'].map(self.norm) == m]
        out=[]
        for _, r in rows.iterrows():
            out.append({
                'characteristic': str(r['characteristic']).strip(),
                'open_close': str(r['open_close']).strip(),
                'binary': str(r['binary']).strip(),
                'possible_values': self.parse_values(r['possible_values']),
                'notes': str(r['Notes']).strip(),
            })
        return out

    def guidelines_for_module(self, module):
        m = self.norm(module)
        rows = self.guidelines[self.guidelines['MODULE NAME'].map(self.norm) == m]
        return [{'characteristic': str(r['CHARACTERISTICS NAME']).strip(), 'guideline': str(r['Guidelines']).strip()} for _, r in rows.iterrows()]

    def guideline_map(self, module):
        return {self.norm(x['characteristic']): x['guideline'] for x in self.guidelines_for_module(module)}

    def module_examples(self, module, n=5):
        rows = self.dev[self.dev['MODULE'].map(self.norm) == self.norm(module)].head(n)
        return rows.to_dict('records')

    def module_summary(self):
        result=[]
        for m in self.modules:
            chars=self.taxonomy_for_module(m)
            result.append({'module':m,'characteristics':[x['characteristic'] for x in chars]})
        return result

    def context(self, module, examples=4):
        return {
            'module': module,
            'characteristics': self.taxonomy_for_module(module),
            'guidelines': self.guidelines_for_module(module),
            'examples': self.module_examples(module, examples),
        }
