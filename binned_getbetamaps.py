

# taskfilesdir = os.path.expanduser("~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/processed")

# outTask_dir = os.path.expanduser("~/NEW_task_files")

# def pretty_events(taskfilesdir, outTask_dir):
#     #rename "trial_type" column as "condition"
#     taskfiles = [(os.path.splitext(bname(file))[0], pd.read_csv(join(taskfilesdir, file), sep='\t'))
#                  for file in ls(taskfilesdir) if "events" in file and file.endswith(".tsv")]
#     new_events = []

#     for s_task in taskfiles:
#         s_task[1].rename(columns={'trial_type':'condition'}, inplace=True)

#         #add columns to DataFrame
#         numCol = s_task[1].shape[1] 
#         insertCol = [4, numCol+1, numCol+2, numCol+3]
#         colNames = ['trial_type', 'unscanned', 'ctl_miss_hit', 'ctl_miss_ws_cs']
#         colVals = ['TBD', 0, 'TBD', 'TBD']
#         for i in range(0, len(colNames)):
#             s_task[1].insert(loc=insertCol[i], column=colNames[i], value=colVals[i], allow_duplicates=True)

#         #The 'unscanned' column flag trials for which no brain data was acquired.
#         #The scan's duration is shorter than the trial's offset time
#         #(0 = data, 1 = no data)
#         for j in s_task[1][s_task[1]['offset']>scanDur].index:
#             s_task[1].loc[j, 'unscanned']=1

#         #pas trial numbers with zeros (on the left) to preserve trial 
#         #temporal order when trials are alphabetized
#         s_task[1]['trial_number'] = s_task[1]['trial_number'].astype('object',
#                                                                copy=False)
#         for k in s_task[1].index:
#             s_task[1].loc[k, 'trial_number'] = str(s_task[1].loc[k, 'trial_number']).zfill(3)

#         #trial_type should have a unique entry per row so that each trial 
#         #can be modelled as a separate condition
#         countEnc = 0
#         countCTL = 0
#         for m in s_task[1][s_task[1]['condition']=='Enc'].index:
#             countEnc = countEnc + 1
#             s_task[1].loc[m, 'trial_type'] = 'Enc'+str(countEnc)
#             if s_task[1].loc[m, 'position_accuracy'] == 0:
#                 s_task[1].loc[m, 'ctl_miss_hit']='missed'
#                 s_task[1].loc[m, 'ctl_miss_ws_cs']='missed'
#             elif s_task[1].loc[m, 'position_accuracy'] == 1:
#                 s_task[1].loc[m, 'ctl_miss_hit']='hit'
#                 s_task[1].loc[m, 'ctl_miss_ws_cs']='wrongsource'
#             elif s_task[1].loc[m, 'position_accuracy'] == 2:
#                 s_task[1].loc[m, 'ctl_miss_hit']='hit'
#                 s_task[1].loc[m, 'ctl_miss_ws_cs']='correctsource' 
#         for n in s_task[1][s_task[1]['condition']=='CTL'].index:
#             countCTL = countCTL + 1
#             s_task[1].loc[n, 'trial_type'] = 'CTL'+str(countCTL)
#             s_task[1].loc[n, 'ctl_miss_hit']='control'
#             s_task[1].loc[n, 'ctl_miss_ws_cs']='control'

#         #78 encoding and 39 control trials if full scan
#         print('Number of encoding trials:  ', countEnc)
#         print('Number of control trials:  ', countCTL)

#         #Export Dataframe to events.tsv file    
#         s_task[1].to_csv(outTask_dir+'/sub-'+id+'_events.tsv',
#                       sep='\t', header=True, index=False)

#         #keep only trials for which fMRI data was collected
#         s_task[1] = s_task[1][s_task[1]['unscanned']==0]

#         #Save vectors of trial labels (e.g., encoding vs control)
#         #to label trials for classification analyses
#         ttypes1 = s_task[1]['condition']
#         ttypes1.to_csv(outTask_dir+'/sub-'+id+'_enco_ctl.tsv',
#                        sep='\t', header=True, index=False)

#         ttypes2 = s_task[1]['ctl_miss_hit']
#         ttypes2.to_csv(outTask_dir+'/sub-'+id+'_ctl_miss_hit.tsv',
#                        sep='\t', header=True, index=False)

#         ttypes3 = s_task[1]['ctl_miss_ws_cs']
#         ttypes3.to_csv(outTask_dir+'/sub-'+id+'_ctl_miss_ws_cs.tsv',
#                        sep='\t', header=True, index=False)

#         new_events.append([(s_task[0], s_task[1]), ttypes1, ttypes2, ttypes3])
#     #from s_task[1] dataframe, create an events dataframe to create a design matrix 
#     #that will be inputed into a first-level model in nistats
#     ev_cols = ['onset', 'duration', 'trial_type', 'condition', 'ctl_miss_hit', 
#                'ctl_miss_ws_cs', 'trial_number']
#     all_events = s_task[1][ev_cols]
#     return new_events, all_events

# #specify path to directory with task files (eventually on Stark)
# # taskdir = '~/../../data/cisl/DATA/cimaq_03-19/derivatives/CIMAQ_fmri_memory/data/task_files/processed'
# # #specify output directory
# # outputdir = '/Users/mombot/Documents/Simexp/CIMAQ/Data/Nistats/Events'

# #rename "trial_type" column as "condition"
# # stask.rename(columns={'trial_type':'condition'}, inplace=True)

# #add columns to DataFrame
# numCol = stask.shape[1] 
# insertCol = [4, numCol+1, numCol+2, numCol+3]
# colNames = ['trial_type', 'unscanned', 'ctl_miss_hit', 'ctl_miss_ws_cs']
# colVals = ['TBD', 0, 'TBD', 'TBD']
# for i in range(0, len(colNames)):
#     stask.insert(loc=insertCol[i], column=colNames[i], value=colVals[i], allow_duplicates=True)

# #The 'unscanned' column flag trials for which no brain data was acquired.
# #The scan's duration is shorter than the trial's offset time
# #(0 = data, 1 = no data)

# for j in stask[stask['offset']>scanDur].index:
#     stask.loc[j, 'unscanned']=1

# #pass trial numbers with zeros (on the left) to preserve trial 
# #temporal order when trials are alphabetized
# # stask['trial_number'] = stask['trial_number'].astype('object',
# #                                                        copy=False)
# # for k in stask.index:
# #     stask.loc[k, 'trial_number'] = str(stask.loc[k, 'trial_number']).zfill(3)

# #trial_type should have a unique entry per row so that each trial 
# #can be modelled as a separate condition
# countEnc = 0
# countCTL = 0
# for m in stask[stask['condition']=='Enc'].index:
#     countEnc = countEnc + 1
#     stask.loc[m, 'trial_type'] = 'Enc'+str(countEnc)
#     if stask.loc[m, 'position_accuracy'] == 0:
#         stask.loc[m, 'ctl_miss_hit']='missed'
#         stask.loc[m, 'ctl_miss_ws_cs']='missed'
#     elif stask.loc[m, 'position_accuracy'] == 1:
#         stask.loc[m, 'ctl_miss_hit']='hit'
#         stask.loc[m, 'ctl_miss_ws_cs']='wrongsource'
#     elif stask.loc[m, 'position_accuracy'] == 2:
#         stask.loc[m, 'ctl_miss_hit']='hit'
#         stask.loc[m, 'ctl_miss_ws_cs']='correctsource' 
# for n in stask[stask['condition']=='CTL'].index:
#     countCTL = countCTL + 1
#     stask.loc[n, 'trial_type'] = 'CTL'+str(countCTL)
#     stask.loc[n, 'ctl_miss_hit']='control'
#     stask.loc[n, 'ctl_miss_ws_cs']='control'

# #78 encoding and 39 control trials if full scan
# print('Number of encoding trials:  ', countEnc)
# print('Number of control trials:  ', countCTL)

# #Export Dataframe to events.tsv file    
# stask.to_csv(outputdir+'/sub-'+id+'_events.tsv',
#               sep='\t', header=True, index=False)
    
# #keep only trials for which fMRI data was collected
# stask = stask[stask['unscanned']==0]

# #Save vectors of trial labels (e.g., encoding vs control)
# #to label trials for classification analyses
# ttypes1 = stask['condition']
# ttypes1.to_csv(outputdir+'/sub-'+id+'_enco_ctl.tsv',
#               sep='\t', header=True, index=False)

# ttypes2 = stask['ctl_miss_hit']
# ttypes2.to_csv(outputdir+'/sub-'+id+'_ctl_miss_hit.tsv',
#               sep='\t', header=True, index=False)

# ttypes3 = stask['ctl_miss_ws_cs']
# ttypes3.to_csv(outputdir+'/sub-'+id+'_ctl_miss_ws_cs.tsv',
#               sep='\t', header=True, index=False)


# #from stask dataframe, create an events dataframe to create a design matrix 
# #that will be inputed into a first-level model in nistats
# ev_cols = ['onset', 'duration', 'trial_type', 'condition', 'ctl_miss_hit', 
#            'ctl_miss_ws_cs', 'trial_number']
# all_events = stask[ev_cols]  

# print(all_events.shape)
# print(all_events.iloc[0:30, :])
