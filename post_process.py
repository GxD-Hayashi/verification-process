import os
import sys
import glob
import pandas as pd
import numpy as np
from pathlib import Path
from openpyxl import load_workbook

workdir = os.path.dirname(__file__)
ewes_sample = [  f for f in glob.glob(os.path.join(workdir, 'CD_[0-9][0-9]_[0-9][0-9][0-9][0-9][0-9]_*[0-9]')) if os.path.isdir(f) ]
wts_sample = [  f for f in glob.glob(os.path.join(workdir, 'CR_[0-9][0-9]_[0-9][0-9][0-9][0-9][0-9]_*[0-9]')) if os.path.isdir(f) ]

out_file = os.path.join(workdir, 'summarized.xlsx')
target_merge, cnv_merge, msi_merge, tmb_merge = None, None, None, None
fusion_merge, splice_merge = None, None

def merge_stat(merge_data, data):
    if merge_data is None :
        merge_data = data
    else:
        merge_data = pd.concat([merge_data, data], axis=0)
    return merge_data

def output_sheet(out_file, data, sheet_name):
    if not data is None :
        try :
            with pd.ExcelWriter(out_file, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer :
                data.to_excel(writer, sheet_name=sheet_name, index=False)
        except FileNotFoundError:
            with pd.ExcelWriter(out_file, engine="openpyxl") as writer :
                data.to_excel(writer, sheet_name=sheet_name, index=False)

for sample in ewes_sample :

    sample_id = os.path.basename(sample)
    cnv_file = os.path.join( sample, 'Summary', sample_id + '.summarized.cnv.exome.tsv')
    msi_file = os.path.join( sample, 'Summary', sample_id + '.summarized.msi.exome.tsv')
    tmb_file = os.path.join( sample, 'Summary', sample_id + '.summarized.tmb.exome.tsv')
    target_file = os.path.join(sample, 'Summary', sample_id + '.summarized.snv.target.tsv')

    f_flag = False
    for f_path in [cnv_file, msi_file, tmb_file, target_file] :
        if not os.path.isfile(f_path) : f_flag = True

    if f_flag :
        print('Summary file not created: ' + sample_id)
        continue

    cnv_data = pd.read_csv(cnv_file,sep="\t")
    msi_data = pd.read_csv(msi_file,sep="\t")
    tmb_data = pd.read_csv(tmb_file,sep="\t")
    target_data = pd.read_csv(target_file,sep="\t", low_memory=False, dtype=str)

    msi_data = msi_data[['MSI','Result']].drop_duplicates()
    tmb_data = tmb_data[['TMB','TMB_STATUS']].drop_duplicates()
    cnv_data = cnv_data[ cnv_data['FILTER']=='PASS' ][['Gene_name','TYPE','ONCOKB_ONCOGENICITY','gene.mean.CN']].drop_duplicates().sort_values('Gene_name')

    msi_data.insert(0, 'sample_id', sample_id)
    tmb_data.insert(0, 'sample_id', sample_id)
    if cnv_data.shape[0] > 0 :
        cnv_data.insert(0, 'sample_id', sample_id)
    else :
        cnv_data = None
    
    target_data = target_data.infer_objects(copy=False).fillna(np.nan).replace([np.nan], [None])
    target_data = target_data[['SYMBOL','HGVSc','HGVSp','AF','Clinvar_CLNSIG','ONCOKB_ONCOGENICITY']].drop_duplicates()
    target_data["HGVSc"] = target_data["HGVSc"].str.split(":", expand=True)[1]
    target_data["HGVSp"] = target_data["HGVSp"].str.split(":", expand=True)[1]
    target_data.insert(0, 'sample_id', sample_id)
    target_data['repo'] = ''
    target_filt = (target_data["Clinvar_CLNSIG"].str.contains("Pathogenic|Likely_pathogenic", case=True, na=False) | target_data["ONCOKB_ONCOGENICITY"].str.contains("oncogenic", case=False, na=False))
    target_data.loc[target_filt, 'Report'] = 'PASS'

    cnv_merge = merge_stat(cnv_merge, cnv_data)
    msi_merge = merge_stat(msi_merge, msi_data)
    tmb_merge = merge_stat(tmb_merge, tmb_data)
    target_merge = merge_stat(target_merge, target_data)

output_sheet(out_file, target_merge, "eWES.snv.target")
output_sheet(out_file, cnv_merge, "eWES.cnv")
output_sheet(out_file, msi_merge, "eWES.msi")
output_sheet(out_file, tmb_merge, "eWES.tmb")
    
for sample in wts_sample :

    sample_id = os.path.basename(sample)
    fusion_file = os.path.join(sample, 'Summary', sample_id + '.summarized.fusion.tsv')
    splice_file = os.path.join(sample, 'Summary', sample_id + '.summarized.splice.tsv')

    if os.path.isfile(fusion_file) :
        fs_data = pd.read_csv(fusion_file, sep="\t")
        fs_data = fs_data[['gene1','gene2','chr1','breakpoint_1','chr2','breakpoint_2','max_split_cnt','max_span_cnt']].drop_duplicates().sort_values('gene1').reset_index(drop=True)
        fs_data.insert(0, 'sample_id', sample_id)
    else :
        print('fusion summary file not created: ' + sample_id)
        fs_data = None

    if os.path.isfile(splice_file) :
        sp_data = pd.read_csv(splice_file, sep="\t")
        sp_data = sp_data[ sp_data['FILTER'] == 'PASS' ][['spliceName','discordant_mates','canonical_reads','ratio','tpm_total','tpm_variant']].drop_duplicates()
        sp_data.insert(0, 'sample_id', sample_id)
    else :
        print('splice summary file not created: ' + sample_id)
        sp_data = None

    fusion_merge = merge_stat(fusion_merge, fs_data)
    splice_merge = merge_stat(splice_merge, sp_data)

output_sheet(out_file, fusion_merge, "WTS.fusion")
output_sheet(out_file, splice_merge, "WTS.splice")

