{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "#!/usr/bin/env python\n",
    "# -*- coding: ISO-8859-1 -*-\n",
    "\n",
    "def NEW_prettyevents_iso8859(participants_sheet_path=\"~/extracted_eprime2/participants.tsv\",\n",
    "                    outdir=\"~/cimaq_newsheets\"):\n",
    "# TrialNum ImageID Trial_part  onsetSec  durationSec\n",
    "    maindir = xpu(dname(participants_sheet_path))\n",
    "    \n",
    "# Clear previous attempts\n",
    "    p1 = pd.read_csv(\"~/extracted_eprime_AS_FWF/participants.tsv\",\n",
    "                     sep='\\t').set_index(\"sub-ID\")[[\"sheetpaths\"]]\n",
    "    [shutil.rmtree(join(outdir, row[0])) for row in p1.iterrows()]\n",
    "\n",
    "# Headers for each of the 3 '.txt' files (open-source '.edat2' (E-prime) equivalent)\n",
    "    prefixes = [\"Onset-Event-Encoding_CIMAQ_\", \"Output-Responses-Encoding_CIMAQ_\",\n",
    "                \"Output_Retrieval_CIMAQ_\"]\n",
    "    EncOnsetCols = [\"TrialNum\", \"Condition\", \"TrialNum_perCondi\",\n",
    "                  \"ImageID\", \"Trial_part\", \"onsetSec\", \"durationSec\"]\n",
    "\n",
    "    allsheets = NEW_get_allsheetsdf()\n",
    "\n",
    "    # Initiate empty list for each outputed variable for backup\n",
    "    full_on_eve_enc, retsheets, fixnstimtimes, timings = [], [], [], []\n",
    "    fixsheets, encsheets, s_ids, yallofems = [], [], [], []\n",
    "    \n",
    "    # Create output directories structure\n",
    "    allsheets[\"enc_outpaths\"] = [join(outdir, row[0], \"events\") for row in allsheetsdf.iterrows()]\n",
    "    allsheets[\"ret_outpaths\"] = [join(outdir, row[0], \"behavioral\") for row in allsheetsdf.iterrows()]\n",
    "    [(os.makedirs(join(outdir, row[0], \"events\"), exist_ok=True),\n",
    "     os.makedirs(join(outdir, row[0], \"behavioral\"), exist_ok=True))\n",
    "     for row in allsheetsdf.iterrows()]\n",
    "    def sheetspersub(allsheets, prefixes):\n",
    "        return dict((pre[1], [[(row[0], row[1]['sheetpath'])\n",
    "                                for row in allsheets.iterrows()\n",
    "                                if row[1]['prefix'] == prefixes[pre[0]]]\n",
    "                               for row in p1.iterrows()])\n",
    "                     for pre in in enumerate(prefixes))\n",
    "    encsheetsA = [(row[0], row[1]['sheetpath'])\n",
    "                  for row in allsheets.iterrows()\n",
    "                  if row[1]['prefix'] == prefixes[0]]\n",
    "        \n",
    "    encsheetsB = [row[1]['sheetpath'] for row in allsheets.iterrows() if row[1]['prefix'] == prefixes[1]]\n",
    "        \n",
    "    retsheets = [row[1]['sheetpath'] for row in allsheets.iterrows()if row[1]['prefix'] == prefixes[2]]\n",
    "\n",
    "    # Rows are individual sheets, 3 per participant\n",
    "    for row in allsheetsdf.iterrows():\n",
    "        if row[1]['prefix'] == prefixes[0]:\n",
    "\n",
    "            newsheet = pd.read_fwf(row[1]['sheetpath'], encoding=row[1]['encoding'],\n",
    "                header=None, sep='\\t', names=EncOnsetCols).iloc[6:]\n",
    "\n",
    "            # Identify stimulus & fixation cross as 2 possible conditions of a same trial\n",
    "            # instead of separate (double) trials\n",
    "            stimids = newsheet[[\"ImageID\",\n",
    "                               \"TrialNum_perCondi\"]].drop_duplicates(\\\n",
    "                               subset=[\"ImageID\", \"TrialNum_perCondi\"]).reset_index(drop=True)\n",
    "            s_ids.append((row[0]+\"_\"+row[1]['prefix']+\"_stimids\", stimids))\n",
    "            newsheet.to_excel(join(maindir, \"temp_\"+row[0]+\"_\"+row[1]['prefix']+'.xlsx'))\n",
    "            newsheet = pd.read_excel(join(\\\n",
    "                           maindir, \"temp_\"+row[0]+\"_\"+row[1]['prefix']+'.xlsx')).drop(\\\n",
    "                               ['TrialNum_perCondi', 'Condition'], axis=1)\n",
    "\n",
    "            tempsheet = newsheet[['TrialNum', 'Trial_part', 'onsetSec', 'durationSec']]\n",
    "\n",
    "            # Extract and concatenate relevant info\n",
    "            fixsheet = df([row[1] for row in tempsheet.iterrows()\n",
    "                                  if row[1]['Trial_part'] == 'Fixation'])\n",
    "            timing = tempsheet.loc[[row[0] for row in tempsheet.iterrows()\n",
    "                                     if row[0] not in fixsheet.index]]\n",
    "            fixsheet = fixsheet.rename(columns={\"onsetSec\": \"fixOnsetSec\",\n",
    "                                               \"durationSec\": \"fixDurSec\"})\n",
    "            fixsheet = fixsheet.transpose().iloc[-2:].transpose(\\\n",
    "                           ).reset_index(drop=True)\n",
    "#             fixsheets.append(((row[0]+\"_\"+row[1]['prefix']+\"_fixsheet_\", fixsheet)))\n",
    "\n",
    "            timing = timing.rename(columns={\"onsetSec\": \"stimOnsetSec\",\n",
    "                                            \"durationSec\": \"stimDurSec\"})\n",
    "            timing = timing.transpose().iloc[-2:].transpose().reset_index(drop=True)\n",
    "#             timings.append((row[0]+\"_\"+row[1]['prefix']+\"_timing_\", timing))\n",
    "            fixnstimtime = pd.concat([timing, fixsheet], axis=1, sort=False)\n",
    "#             fixnstimtimes.append((row[0]+\"_\"+row[1]['prefix']+\"_fixnstimtime_\", fixnstimtime))\n",
    "            allofem = pd.concat([fixnstimtime, stimids], axis=1, sort=False)\n",
    "            yallnametuple = (row[0]+\"_\"+row[1]['prefix'], allofem)\n",
    "            yallofems.append(yallnametuple)\n",
    "            row[1]['oldname'] = yallnametuple[0]\n",
    "\n",
    "        if row[1]['prefix'] == prefixes[1]:\n",
    "            encsheet = pd.read_csv(row[1]['sheetpath'],\n",
    "                                   encoding=row[1]['encoding'],\n",
    "                                   header=0,\n",
    "                                   sep='\\t').iloc[3:].fillna(False).rename(\\\n",
    "                           columns={\"TrialNumber\": \"TrialNum\",\n",
    "                                    \"Category\": \"Condition\"}).set_index(\"TrialNum\")\n",
    "            encsheet = encsheet.drop([\"TrialCode\"], axis=1)\n",
    "            encsheet[\"Condition\"] = encsheet[\"Condition\"].astype(\\\n",
    "                                        'str').replace({'CTL': '0', 'Enc': '1'})\n",
    "            encnametuple = (row[0]+\"_\"+row[1]['prefix'],\n",
    "                              encsheet.reset_index(drop=True))\n",
    "            encsheets.append(encnametuple)\n",
    "            row[1]['oldname'] = encnametuple[0]\n",
    "\n",
    "        # Immediately removing last row since it was an Eprime error (St-Laurent, 2019)\n",
    "        if row[1]['prefix'] == prefixes[2]:\n",
    "            retsheet = pd.read_csv(row[1]['sheetpath'],\n",
    "                                   encoding=row[1]['encoding'],\n",
    "                                   header=0, sep='\\t').iloc[:, :-1]\n",
    "            retnametuple = (row[1]['prefix']+\"_\"+row[0],\n",
    "                              retsheet.reset_index(drop=True))\n",
    "            retsheets.append(retnametuple)\n",
    "            row[1]['oldname'] = retnametuple[0]\n",
    "        encoding = tuple(zip(sorted(yallofems), sorted(encsheets)))\n",
    "        fullencsheets = [(item[0][0], pd.concat([item[0][1], item[1][1]], axis=1))\n",
    "                        for item in encoding]\n",
    "            \n",
    "    return sorted(yallofems), sorted(encsheets), sorted(retsheets)\n",
    "\n",
    "def main():\n",
    "    yallofems, encsheets, retsheets = NEW_prettyevents_iso8859()\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    main()\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.6.9"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}