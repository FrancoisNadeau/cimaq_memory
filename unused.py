

# #!/usr/bin/env python3

# from cimaq_utils import *
# from cimaq_utils import loadimages
# from blind_rename import *
# from inspect_misc_text import *
# from zipctl import uzipfiles

# cimaq_dir = xpu('~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives')

# mean_sheets_pathlist = \
# ['~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/MotionResults/fMRI_meanMotion.tsv',
#  '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/MemoTaskParticipantFile.tsv',
#  '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/Neuropsych/ALL_Neuropsych_scores.tsv',
#  '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/Participants_bids.tsv',
#  '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/sub_list_TaskQC.tsv',
#  '~/../../media/francois/seagate_1tb/cimaq_03-19/cimaq_derivatives/participants/TaskResults/fMRI_behavMemoScores.tsv']

# mean_paths = [xpu(spath) for spath in mean_sheets_pathlist]   

# new_mean_dir = join(cimaq_dir, 'mean_sheets')
# new_conf_dir = join(cimaq_dir, 'new_confounds')
# new_events_dir = join(cimaq_dir, 'all_events')
# confdir = join(cimaq_dir, 'confounds')   

# uzeprimes = join(cimaq_dir, 'task_files', 'uzeprimes')
# mean_sheets_patterns = (('dccid', '(?<!\d)\d{6}(?!\d)'),
#                         ('pscid', '(?<!\d)\d{7}(?!\d)'))

# def save_new_sheets(new_mean_dir, new_conf_dir, new_events_dir):
#     os.makedirs(new_mean_dir, exist_ok=True)
#     [sheet[1].to_csv(join(new_mean_dir,
#                           os.path.splitext(bname(sheet[0]))[0]+'.csv'))
#      for sheet in mean_sheets]
#     os.makedirs(new_conf_dir, exist_ok=True)
#     [sheet[1].to_csv(join(new_conf_dir,
#                           os.path.splitext(bname(sheet[0]))[0]+'.csv'))
#      for sheet in new_confounds]
#     os.makedirs(new_events_dir, exist_ok=True)
#     [sheet[1].to_csv(join(new_events_dir,
#                           os.path.splitext(bname(sheet[0]))[0]+'.csv'))
#      for sheet in indiv_sheets]

# def repair_sheets(cimaq_dir, mean_sheets_pathlist, mean_sheets_patterns):
#     uzipfiles(join(cimaq_dir, 'task_files/zipped_eprime'), 'uzeprimes')
#     cimaqfilter()
    
#     counfounds_parsing_infos = df(get_infos(fpaths) for
#                                   fpaths in loadfiles(indir=confdir).fpaths)
    
#     prefixes = pd.Series(('_'.join(val.split('_')[:2])
#                           for val in loadfiles(
#                               indir=uzeprimes).fname)).unique()
#     indiv_patterns = tuple(item for item
#                            in dict(zip(prefixes, prefixes)).items())

#     indiv_parsing_infos = sortmap(df((get_infos(fpath)
#                                       for fpath in loadfiles(indir=uzeprimes).fpaths)),
#                                   indiv_patterns).convert_dtypes()

#     mean_parsing_infos = df((get_infos(fpath) for fpath in
#                              loadfiles(pathlist=mean_paths).fpaths))
    
#     regist_dialects(mean_parsing_infos), regist_dialects(indiv_parsing_infos)

#     mean_sheets = tuple(prep_sheet(filename = row[1]['fpaths'],
#                                    encoding=row[1]['encoding'],
#                                    hdr = row[1]['has_header'],
#                                    n_fields = row[1]['n_fields'],
#                                    delimiter = row[1]['delimiter'],
#                                    dupindex = row[1]['dup_index'],
#                                    row_breaks = row[1]['row_breaks'],
#                                    r_rowbreaks = row[1]['r_rowbreaks'],
#                                    n_lines = row[1]['n_lines'],
#                                    colnames = row[1]['colnames'],
#                                    width = row[1]['width'],
#                                    lineterminator = row[1]['lineterminator'])
#                         for row in mean_parsing_infos.iterrows())

#     mean_sheets_tmp = rename_imposter_cols([sheet[1] for sheet
#                                             in mean_sheets],
#                                            mean_sheets_patterns)
#     mean_sheets = tuple(zip(tuple(item[0] for item in mean_sheets),
#                             mean_sheets_tmp))

#     indiv_sheets = tuple(prep_sheet(filename = row[1]['fpaths'],
#                                     encoding=row[1]['encoding'],
#                               hdr = row[1]['has_header'],
#                               n_fields = row[1]['n_fields'],
#                               delimiter = row[1]['delimiter'],
#                               dupindex = row[1]['dup_index'],
#                               row_breaks = row[1]['row_breaks'],
#                               r_rowbreaks = row[1]['r_rowbreaks'],
#                               n_lines = row[1]['n_lines'],
#                               colnames = row[1]['colnames'],
#                               width = row[1]['width'],
#                               lineterminator = row[1]['lineterminator'])
#                         for row in indiv_parsing_infos.iterrows())

#     new_confounds = tuple(prep_sheet(filename = row[1]['fpaths'],
#                                    encoding=row[1]['encoding'],
#                                    hdr = row[1]['has_header'],
#                                    n_fields = row[1]['n_fields'],
#                                    delimiter = row[1]['delimiter'],
#                                    dupindex = row[1]['dup_index'],
#                                    row_breaks = row[1]['row_breaks'],
#                                    r_rowbreaks = row[1]['r_rowbreaks'],
#                                    n_lines = row[1]['n_lines'],
#                                    colnames = row[1]['colnames'],
#                                    width = row[1]['width'],
#                                    lineterminator = row[1]['lineterminator'])
#                         for row in counfounds_parsing_infos.iterrows())
#     save_new_sheets(new_mean_dir, new_conf_dir, new_events_dir)

# def main():
#     repair_sheets(cimaq_dir, mean_sheets_pathlist, mean_sheets_patterns)

# if __name__ == "__main__":
#     main()
