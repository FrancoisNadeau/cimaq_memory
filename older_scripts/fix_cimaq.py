#!/usr/bin/env python3

from cimaq_utils import *
from cimaq_utils import loadimages
from cimaq_utils import loadfiles
from cimaq_utils import sortmap
from blind_rename import rename_imposter_cols
from inspect_misc_text import *
from zipctl import uzipfiles
from get_infos import get_infos
from os.path import expanduser as xpu
from os.path import join as pjoin
from collections import OrderedDict

def get_cimaq_dir_paths(cimaq_dir=None):
    json_params = json_read(xpu('~/cimaq_memory/cimaq_dir_list.json'), 'r')
    cimaq_dir = next((xpu(cimaq_dir) if cimaq_dir
                      else xpu(json_params['cimaq_dir'][0])))
    dir_list = dict(((itm[0], [pjoin(cimaq_dir, subitm)
                            for subitm in itm[1].__iter__()])
                  for itm in json_params['dir_list'].items()))
    patterns = df(tuple((itm[0], itm[1]) for itm in
                        json_params['patterns'].items()),
                            columns=['ids', 'patterns'])
                  
    return dir_list, patterns

def fix_cimaq(cimaq_dir):
    # Paths to files and direcotries
    cimaq_dir = xpu(cimaq_dir)
    dlst, patterns = get_cimaq_dir_paths(cimaq_dir)

    # Name and indexing patterns and prefixes
    prefixes = pd.Series(('_'.join(val.split('_')[:2])
                          for val in loadfiles(loadimages(dlst['uzeprimes'][0])).fname)).unique()
    indiv_patterns = tuple(item for item
                               in dict(zip(prefixes, prefixes)).items())
    
    # Structure file paths and participant identifiers in a DataFrame
    events_sheets = loadfiles(loadimages(dlst['uzeprimes'][0]))
    confounds_sheets = loadfiles(loadimages(dlst['confdir'][0]))
    events_sheets[patterns.ids[1]] = [re.compile(patterns.patterns[1]).search(fname).group()
                       for fname in events_sheets.fname]
    confounds_sheets[patterns.ids[0]] = [re.compile(patterns.patterns[0]).search(fname).group()
                       for fname in loadfiles(loadimages(dlst['confdir'][0])).fname]
    
    # Get parsing, dialect and encoding information with 'get_infos' function
    events_infos = df((get_infos(fpath) for fpath in events_sheets.fpaths))
    confounds_infos = df((get_infos(fpath) for fpath in confounds_sheets.fpaths))
    events_infos = sortmap(pd.merge(events_infos, events_sheets,
                                    how='outer'), indiv_patterns)
    confounds_infos = pd.merge(confounds_infos, confounds_sheets, how='outer')
    mean_parsing_infos = df((get_infos(fpath) for fpath in
                             loadfiles(dlst['mean_paths']).fpaths))
    
    # Group information about participants who passed QC assessment
    new_mean_sheets = OrderedDict((row[1]['fpaths'],
                                   prep_sheet(filename = row[1]['fpaths'],
                                encoding=row[1]['encoding'],
                                hdr = row[1]['has_header'],
                                n_fields = row[1]['n_fields'],
                                delimiter = row[1]['delimiter'],
                                dupindex = row[1]['dup_index'],
                                row_breaks = row[1]['row_breaks'],
                                r_rowbreaks = row[1]['r_rowbreaks'],
                                n_lines = row[1]['n_lines'],
                                width = row[1]['width'],
                                lineterminator = row[1]['lineterminator']))
                     for row in mean_parsing_infos.iterrows())
    new_mean_sheets = dict(zip(new_mean_sheets.keys(),
                               tuple(sheet.convert_dtypes(str)
                                     for sheet in rename_imposter_cols(
                   [sheet for sheet in new_mean_sheets.values()],
                   mean_sheets_patterns))))
    min_ind = df([sheet.dccid for sheet in new_mean_sheets.values()
               if sheet.shape[0] == pd.Series(
                   [sheet.shape[0] for sheet in
                    new_mean_sheets.values()]).min()]).T
    inds = [sheet[1].dccid.tolist() for sheet in new_mean_sheets.items()]
    new_mean_sheets = dict((item[0], item[1].set_index(
                          patterns.ids[0]).loc[min_ind.dccid].reset_index(drop=False))
                           for item in new_mean_sheets.items())
    renamer = [sheet[[patterns.ids[0], patterns.ids[1]]] for sheet in new_mean_sheets.values()
               if patterns.ids[0] and patterns.ids[1] in sheet.columns][0].astype(str).dropna()
    events_infos = pd.merge(events_infos, renamer, on=patterns.ids[1], how='outer').dropna(how='any')
    confounds_infos = pd.merge(confounds_infos, renamer, on=patterns.ids[0], how='outer').dropna(how='any')
    all_infos = pd.concat([events_infos, confounds_infos]).fillna(False).reset_index(drop=True)
    all_infos['confounds'] = ['confounds' in fname for fname in all_infos.fname]
    all_infos['prefix'] = [find_key(row[1][['output_responses', 'onset_event',
                               'output_retrieval', 'confounds']].T.to_dict(), True)
                           for row in all_infos.iterrows()]
    all_infos.to_csv(pjoin(cimaq_dir, 'all_parsing_infos.csv'), index=False)

    # Use 'prep_sheet' function to fix errors by reading data as a stream of bytes
    new_events = tuple((''.join(['sub-', row[1][patterns.ids[1]], '-', row[1][patterns.ids[0]],
                                '_', row[1]['prefix'], '.csv']),
                        prep_sheet(filename = row[1]['fpaths'],
                                   encoding=row[1]['encoding'],
                                   hdr = row[1]['has_header'],
                                   n_fields = row[1]['n_fields'],
                                   delimiter = row[1]['delimiter'],
                                   dupindex = row[1]['dup_index'],
                                   row_breaks = row[1]['row_breaks'],
                                   r_rowbreaks = row[1]['r_rowbreaks'],
                                   n_lines = row[1]['n_lines'],
                                   width = row[1]['width'],
                                   lineterminator = row[1]['lineterminator']))
                       for row in tqdm(all_infos.iterrows()))
    newdir = pjoin(cimaq_dir, 'cleaned_events_and_confounds')
    os.makedirs(newdir, exist_ok=True)
    next((itm[1].to_csv(pjoin(newdir, itm[0]), index=False)
          for itm in new_events))
    
def main():
    fix_cimaq(cimaq_dir = '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives')

if __name__ == "__main__":
    main()
