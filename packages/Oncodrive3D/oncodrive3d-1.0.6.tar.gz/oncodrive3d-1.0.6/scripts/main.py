#!/usr/bin/env python

"""
Oncodrive3D is a fast and accurate computational method designed to analyze 
patterns of somatic mutation across tumors, with the goal of identifying 
three-dimensional (3D) clusters of missense mutations and detecting genes 
under positive selection. 
"""

import os
import click
import daiquiri
import numpy as np

from scripts import __logger_name__, __version__
from scripts.globals import DATE, setup_logging_decorator, startup_message

logger = daiquiri.getLogger(__logger_name__)


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__)
def oncodrive3D():
    """
    Oncodrive3D: software for the identification of 3D-clustering 
    of missense mutations for cancer driver genes detection.
    """
    pass


# =============================================================================
#                               BUILD DATASETS
# =============================================================================

@oncodrive3D.command(context_settings=dict(help_option_names=['-h', '--help']),
                     help="Build datasets - Required (once) after installation.")
@click.option("-o", "--output_dir", 
              help="Directory where to save the files", type=str, default='datasets')
@click.option("-s", "--organism", type=click.Choice(["Homo sapiens", 'human', "Mus musculus", 'mouse']), 
              help="Organism name", default="Homo sapiens")
@click.option("-m", "--mane", 
              help="Use structures predicted from MANE Select transcripts (Homo sapiens only)", is_flag=True)
@click.option("-M", "--mane_only", 
              help="Use only structures predicted from MANE Select transcripts", is_flag=True)
@click.option("-C", "--custom_mane_pdb_dir", 
              help="Directory where to load custom MANE PDB structures (overwriting existing ones)")
@click.option("-f", "--custom_mane_metadata_path", 
              help="Path to a dataframe including the Ensembl Protein ID and the amino acid sequence of the custom MANE PDB structures")
@click.option("-j", "--mane_version", default=1.4, 
              help="Version of the MANE Select release from NCBI")
@click.option("-d", "--distance_threshold", type=click.INT, default=10,
              help="Distance threshold (Å) to define contact between amino acids")
@click.option("-c", "--cores", type=click.IntRange(min=1, max=len(os.sched_getaffinity(0)), clamp=False), default=len(os.sched_getaffinity(0)),
              help="Number of cores to use in the computation")
@click.option("--af_version", type=click.IntRange(min=1, max=4, clamp=False), default=4,
              help="Version of AlphaFold 2 predictions")
@click.option("-y", "--yes", 
              help="No interaction", is_flag=True)
@click.option("-v", "--verbose", 
              help="Verbose", is_flag=True)
@setup_logging_decorator
def build_datasets(output_dir,
                   organism,
                   mane,
                   mane_only,
                   custom_mane_pdb_dir,
                   custom_mane_metadata_path,
                   distance_threshold,
                   cores, 
                   af_version,
                   mane_version,
                   yes,
                   verbose):
    """"Build datasets necessary to run Oncodrive3D."""
    
    from scripts.datasets.build_datasets import build
    
    startup_message(__version__, "Initializing building datasets..")
    if mane_only:
        mane = True
    
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Build folder path: {output_dir}")
    logger.info(f"Organism: {organism}")
    logger.info(f"MANE Select: {mane}")
    logger.info(f"MANE Select only: {mane_only}")
    logger.info(f"Custom MANE PDB directory: {custom_mane_pdb_dir}")
    logger.info(f"Custom MANE PDB metadata path: {custom_mane_metadata_path}")
    logger.info(f"Distance threshold: {distance_threshold}Å")
    logger.info(f"CPU cores: {cores}")
    logger.info(f"AlphaFold version: {af_version}")
    logger.info(f"MANE version: {mane_version}")
    logger.info(f"Verbose: {verbose}")
    logger.info(f'Log path: {os.path.join(output_dir, "log")}')
    logger.info("")
    
    build(
        output_dir,
        organism,
        mane,
        mane_only,
        custom_mane_pdb_dir,
        custom_mane_metadata_path,
        distance_threshold,
        cores,
        af_version,
        mane_version
        )



# =============================================================================
#                                     RUN
# =============================================================================

@oncodrive3D.command(context_settings=dict(help_option_names=['-h', '--help']),
                     help="Run 3D-clustering analysis.")
@click.option("-i", "--input_path", type=click.Path(exists=True), required=True, 
              help="Path of the MAF file (or direct VEP output) used as input")
@click.option("-p", "--mut_profile_path", type=click.Path(exists=True), 
              help="Path of the mutation profile (192 trinucleotide contexts) used as optional input")
@click.option("-m", "--mutability_config_path", type=click.Path(exists=True), 
              help="Path of the config file with information on mutability")
@click.option("-o", "--output_dir", type=str, default='output', 
              help="Path to output directory")
@click.option("-d", "--data_dir", type=click.Path(exists=True), default = os.path.join('datasets'), 
              help="Path to datasets")
@click.option("-n", "--n_iterations", type=int, default=10000, 
              help="Number of densities to be simulated")
@click.option("-a", "--alpha", type=float, default=0.01, 
              help="Significant threshold for the p-value of res and gene")
@click.option("-P", "--cmap_prob_thr", type=float, default=0.5,
              help="Threshold to define AAs contacts based on distance on predicted structure and PAE")
@click.option("-c", "--cores", type=click.IntRange(min=1, max=len(os.sched_getaffinity(0)), clamp=False), default=len(os.sched_getaffinity(0)),
              help="Set the number of cores to use in the computation")
@click.option("-s", "--seed", type=int,
              help="Set seed to ensure reproducible results")
@click.option("-v", "--verbose", 
              help="Verbose", is_flag=True)
@click.option("-t", "--cancer_type", 
              help="Cancer type", type=str)
@click.option("-C", "--cohort", 
              help="Name of the cohort", type=str)
@click.option("--no_fragments", is_flag=True, 
              help="Disable processing of fragmented (AF-F) proteins")
@click.option("--only_processed", is_flag=True,
              help="Include only processed genes in the output")
@click.option("--thr_mapping_issue", type=float, default=0.1,
              help="Threshold to filter out genes by the ratio of mutations with mapping issue (out of structure, WT AA mismatch, zero prob to mutate). Threshold of 1 disable any WT AA mismatch mutations filtering.")
@click.option("--o3d_transcripts", is_flag=True,
              help="Filter mutations by keeping transcripts included in Oncodrive3D built sequence dataframe. Only if input file (--i) is a raw VEP output")
@click.option("--use_input_symbols", is_flag=True,
              help="Update HUGO symbols in Oncodrive3D built datasets by using input file entries. Only if input file (--i) is a raw VEP output")
@click.option("--mane", is_flag=True,
              help="If multiple structures are associated to the same HUGO symbol in the input file, use the MANE ones.")
@click.option("--sample_info", is_flag=True,
              help="Include sample information in position-level result (currently unavailable).")                  # TODO: enable sample info in output
@setup_logging_decorator
def run(input_path,
        mut_profile_path,
        mutability_config_path,
        output_dir,
        data_dir,
        n_iterations,
        alpha,
        cmap_prob_thr,
        cores,
        seed,
        verbose,
        cancer_type,
        cohort,
        no_fragments,
        only_processed,
        thr_mapping_issue,
        o3d_transcripts,
        use_input_symbols,
        mane,
        sample_info):
    """Run Oncodrive3D."""
    
    from scripts.run.clustering import run_clustering
    
    # Initialize
    plddt_path = os.path.join(data_dir, "confidence.tsv")
    cmap_path = os.path.join(data_dir, "prob_cmaps")
    seq_df_path = os.path.join(data_dir, "seq_for_mut_prob.tsv")
    pae_path = os.path.join(data_dir, "pae")
    cancer_type = cancer_type if cancer_type else np.nan
    cohort = cohort if cohort else f"cohort_{DATE}"
    path_prob = mut_profile_path if mut_profile_path else "Not provided, mutabilities will be used" if mutability_config_path else "Not provided, uniform distribution will be used"
    path_mutability_config = mutability_config_path if mutability_config_path else "Not provided, mutabilities will not be used"

    # Log
    startup_message(__version__, "Initializing analysis..")

    logger.info(f"Input MAF: {input_path}")
    logger.info(f"Input mut profile: {path_prob}")
    logger.info(f"Input mutability config: {path_mutability_config}")
    logger.info(f"Build directory: {data_dir}")
    logger.info(f"Output directory: {output_dir}")
    logger.debug(f"Path to CMAPs: {cmap_path}")
    logger.debug(f"Path to DNA sequences: {seq_df_path}")
    logger.debug(f"Path to PAE: {pae_path}")
    logger.debug(f"Path to pLDDT scores: {plddt_path}")
    logger.info(f"CPU cores: {cores}")
    logger.info(f"Iterations: {n_iterations}")
    logger.info(f"Significant level: {alpha}")
    logger.info(f"Probability threshold for CMAPs: {cmap_prob_thr}")
    logger.info(f"Cohort: {cohort}")
    logger.info(f"Cancer type: {cancer_type}")
    logger.info(f"Disable fragments: {no_fragments}")
    logger.info(f"Output only processed genes: {only_processed}")
    logger.info(f"Ratio threshold mutations with mapping issue: {thr_mapping_issue}")
    logger.info(f"Seed: {seed}")
    logger.info(f"Filter input by Oncodrive3D transcripts: {o3d_transcripts}")
    logger.info(f"Use HUGO symbols of input file: {use_input_symbols}")
    logger.info(f"Prioritize MANE transcripts when using input HUGO symbols: {mane}")
    logger.info(f"Include sample informations in output: {sample_info}")
    logger.info(f"Verbose: {verbose}")
    logger.info(f'Log path: {os.path.join(output_dir, "log")}')
    logger.info("")

    run_clustering(input_path,
                    mut_profile_path,
                    mutability_config_path,
                    output_dir,  
                    cmap_path,
                    seq_df_path,
                    plddt_path,
                    pae_path,                    
                    n_iterations,
                    alpha,
                    cmap_prob_thr,
                    cores,
                    seed,
                    verbose,
                    cancer_type,
                    cohort,
                    no_fragments,
                    only_processed,
                    thr_mapping_issue,
                    o3d_transcripts,
                    use_input_symbols,
                    mane,
                    sample_info)

               

# =============================================================================
#                              BUILD ANNOTATIONS
# =============================================================================

@oncodrive3D.command(context_settings=dict(help_option_names=['-h', '--help']),
               help="Build annotations - Required (once) only to plot annotations.")
@click.option("-d", "--data_dir", help="Path to datasets", type=str, required=True)
@click.option("-o", "--output_dir", help="Path to dir where to store annotations", type=str, default="annotations")
@click.option("-g", "--ddg_dir", help="Path to custom ddG predictions", type=str)
#@click.option("-S", "--path_pdb_tool_sif", help="Path to the PDB_Tool SIF", type=str, required=True) 
@click.option("-s", "--organism", type=click.Choice(["Homo sapiens", 'human', "Mus musculus", 'mouse']), help="Organism name", default="Homo sapiens")
@click.option("-c", "--cores", type=click.IntRange(min=1, max=len(os.sched_getaffinity(0)), clamp=False), default=len(os.sched_getaffinity(0)),
              help="Number of cores to use in the computation")
@click.option("-y", "--yes", help="No interaction", is_flag=True)
@click.option("-v", "--verbose", help="Verbose", is_flag=True)
@setup_logging_decorator
def build_annotations(data_dir,
                      output_dir,
                      ddg_dir,
                      #path_pdb_tool_sif,
                      organism,
                      cores,
                      yes,
                      verbose):
    """
    Build datasets to plot protein annotations.
    """

    startup_message(__version__, "Initializing building annotations..")
    
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Path to datasets: {data_dir}")
    logger.info(f"Path to custom ddG predictions: {ddg_dir}")
    #logger.info(f"Path to PDB_Tool SIF: {path_pdb_tool_sif}")
    logger.info(f"Organism: {organism}")
    logger.info(f"Cores: {cores}")
    logger.info(f"Verbose: {bool(verbose)}")
    logger.info(f'Log path: {os.path.join(output_dir, "log")}')
    logger.info("")
    
    from scripts.plotting.build_annotations import get_annotations

    get_annotations(data_dir, 
                    output_dir, 
                    ddg_dir,
                    #path_pdb_tool_sif,
                    organism,
                    cores)



# =============================================================================
#                                    PLOT
# =============================================================================

@oncodrive3D.command(context_settings=dict(help_option_names=['-h', '--help']),
               help="Generate plots for a quick interpretation of the 3D-clustering analysis.")
@click.option("-g", "--gene_result_path", type=click.Path(exists=True), required=True,
              help="Path to genes-level O3D result")
@click.option("-p", "--pos_result_path", type=click.Path(exists=True), required=True,
              help="Path to positions-level O3D result")
@click.option("-i", "--maf_path", type=click.Path(exists=True), required=True,
              help="Path to input mutations file")
@click.option("-m", "--miss_prob_path", type=click.Path(exists=True), required=True,
              help="Path to missense mutations probability dictionary")
@click.option("-s", "--seq_df_path", type=click.Path(exists=True), required=True,
              help="Path to dataframe of sequences")
@click.option("-d", "--datasets_dir", type=click.Path(exists=True), required=True,
              help="Path to datasets directory")
@click.option("-a", "--annotations_dir", type=click.Path(exists=True), required=True, 
              help="Path to annotations directory")
@click.option("-o", "--output_dir", default="./",
              help="Path to output directory where to save plots")
@click.option("-c", "--cohort", 
              help="Cohort name", type=str, required=True)
@click.option("--fdr",                                                                             
              help="Show p-values as BH FDR corrected", type=str)
@click.option("--maf_for_nonmiss_path", type=click.Path(exists=True), 
              help="Path to input mutations file including non-missense mutations")
@click.option("--lst_summary_tracks", type=str,
              help="List of tracks to be included in the summary plot (e.g., score,miss_count,clusters)", 
              default="score,miss_count,res_count,res_clust_mut,clusters")
@click.option("--lst_summary_hratios", type=str,
              help="List of float to define horizontal ratio of each track of the summary plot") 
@click.option("--lst_gene_tracks", type=str,
              help="List of tracks to be included in the gene plots (e.g., miss_count,miss_prob,score)",
              default="miss_count,miss_prob,score,clusters,ddg,disorder,pacc,ptm,site,sse,pfam,prosite,membrane,motif")
@click.option("--lst_gene_hratios", type=str,
              help="List of floats to define horizontal ratio of each track of the gene plot") 
@click.option("--summary_fsize_x", help="Figure size x-axis for summary plots (dynamically adjusted)", type=float, default=0.5)
@click.option("--summary_fsize_y", help="Figure size y-axis for summary plots", type=int, default=8)
@click.option("--gene_fsize_x", help="Figure size x-axis for gene plots", type=int, default=24)
@click.option("--gene_fsize_y", help="Figure size y-axis for gene plots", type=int, default=12)
@click.option("--summary_alpha", help="Alpha value for score track in summary plot", type=float, default=0.7)
@click.option("--dist_thr", help="Threshold of ratios to avoid clashing feature names (e.g., domains and motifs)", type=float, default=0.1)
@click.option("--genes", help="List of genes to be analysed in the report (e.g., --genes TP53,KRAS,PIK3CA)", type=str)
@click.option("--c_genes_only", help="Generate gene plots only for significant genes (use --no-c_genes_only to disable)", is_flag=True, default=True)
@click.option("--max_n_genes", help="Max number of genes to plot", type=int, default=30)
@click.option("--volcano_top_n", help="Top associations to annotate in volcano plot", type=int, default=15)
@click.option("--volcano_fsize_x", help="Figure size x-axis for volcano plot", type=float, default=10)
@click.option("--volcano_fsize_y", help="Figure size y-axis for volcano plot", type=float, default=6)
@click.option("--volcano_subplots_fsize_x", help="Figure size x-axis for volcano subplots (dynamically adjusted)", type=float, default=3.2)
@click.option("--volcano_subplots_fsize_y", help="Figure size y-axis for volcano subplots (dynamically adjusted)", type=float, default=3)
@click.option("--log_odds_fsize_x", help="Figure size x-axis for log odds plot (dynamically adjusted)", type=float, default=1.7)
@click.option("--log_odds_fsize_y", help="Figure size y-axis for log odds plot (dynamically adjusted)", type=float, default=3.6)
@click.option("--output_csv", help="Output csv file including annotated Oncodrive3D result", is_flag=True)
@click.option("--output_all_pos", help="Include all position (including non-mutated ones) in the Oncodrive3D enriched result", is_flag=True)
@click.option("-v", "--verbose", help="Verbose", is_flag=True)
@setup_logging_decorator
def plot(gene_result_path,
         pos_result_path,
         maf_path,
         miss_prob_path,
         seq_df_path,
         datasets_dir,
         annotations_dir,
         output_dir,
         cohort,
         fdr,
         maf_for_nonmiss_path,
         lst_summary_tracks,
         lst_summary_hratios,
         lst_gene_tracks,
         lst_gene_hratios,
         summary_fsize_x,
         summary_fsize_y,
         gene_fsize_x,
         gene_fsize_y,
         summary_alpha,
         dist_thr, 
         genes,
         c_genes_only,
         max_n_genes,
         volcano_top_n,
         volcano_fsize_x,
         volcano_fsize_y,
         volcano_subplots_fsize_x,
         volcano_subplots_fsize_y,
         log_odds_fsize_x,
         log_odds_fsize_y,
         output_csv,
         output_all_pos,
         verbose):
    """"Generate summary and individual gene plots for a quick interpretation of the 3D-clustering analysis."""

    from scripts.plotting.plot import generate_plots
    from scripts.plotting.utils import init_plot_pars, parse_lst_tracks

    startup_message(__version__, "Starting plot generation..")
    logger.info(f"O3D genes-result: {gene_result_path}")
    logger.info(f"O3D positions-result: {pos_result_path}")
    logger.info(f"O3D input mutations: {maf_path}")
    logger.info(f"O3D missense mut prob: {miss_prob_path}")
    logger.info(f"O3D sequences df: {seq_df_path}")
    logger.info(f"O3D datasets: {datasets_dir}")
    logger.info(f"O3D annotations: {annotations_dir}")
    logger.info(f"Output: {output_dir}")
    logger.info(f"Cohort: {cohort}")
    logger.info(f"Use FDR: {fdr}")
    logger.info(f"Input mutations including non-missense: {maf_for_nonmiss_path}")     
    logger.info(f"Custom summary plot tracks: {lst_summary_tracks}")
    logger.debug(f"Custom summary plot h-ratios: {lst_summary_hratios}")
    logger.debug(f"Custom gene plots tracks: {lst_gene_tracks}")
    logger.debug(f"Custom gene plots h-ratios: {lst_gene_hratios}")
    logger.debug(f"Summary plot fsize_x (dynamically adjusted): {summary_fsize_x}")
    logger.debug(f"Summary plot fsize_y: {summary_fsize_y}")
    logger.debug(f"Gene plots fsize_x: {gene_fsize_x}")
    logger.debug(f"Gene plots fsize_y: {gene_fsize_y}")
    logger.debug(f"Volcano plot fsize_x: {volcano_fsize_x}")
    logger.debug(f"Volcano plot fsize_y: {volcano_fsize_y}")
    logger.debug(f"Volcano subplot fsize_x (dynamically adjusted): {volcano_subplots_fsize_x}")
    logger.debug(f"Volcano subplot fsize_y (dynamically adjusted): {volcano_subplots_fsize_y}")
    logger.debug(f"Log odds plot fsize_x (dynamically adjusted): {log_odds_fsize_x}")
    logger.debug(f"Log odds plot fsize_y (dynamically adjusted): {log_odds_fsize_y}")
    logger.info(f"Summary plot score alpha: {summary_alpha}")
    logger.debug(f"Threshold for clashing feat: {dist_thr}")
    logger.info(f"Subset of genes: {genes}")
    logger.info(f"Gene plots for significant genes only: {bool(c_genes_only)}")
    logger.info(f"Max number of genes to plot: {max_n_genes}")
    logger.info(f"Volcano plot top associations to annotate: {volcano_top_n}")
    logger.info(f"Output csv file: {bool(output_csv)}")
    logger.info(f"Include non-mutated positions in csv file: {bool(output_all_pos)}")
    logger.info(f"Verbose: {bool(verbose)}")
    logger.info(f'Log path: {os.path.join(output_dir, "log")}')
    logger.info("")

    lst_summary_tracks = parse_lst_tracks(lst_summary_tracks, plot_type="summary")
    lst_gene_tracks = parse_lst_tracks(lst_gene_tracks, plot_type="gene")
    plot_pars = init_plot_pars(summary_fsize_x=summary_fsize_x,
                               summary_fsize_y=summary_fsize_y,
                               gene_fsize_x=gene_fsize_x, 
                               gene_fsize_y=gene_fsize_y, 
                               volcano_fsize_x=volcano_fsize_x,
                               volcano_fsize_y=volcano_fsize_y,
                               volcano_subplots_fsize_x=volcano_subplots_fsize_x,
                               volcano_subplots_fsize_y=volcano_subplots_fsize_y,
                               log_odds_fsize_x=log_odds_fsize_x,
                               log_odds_fsize_y=log_odds_fsize_y,
                               dist_thr=dist_thr,
                               summary_alpha=summary_alpha,
                               lst_summary_tracks=lst_summary_tracks,
                               lst_summary_hratios=lst_summary_hratios,
                               lst_gene_annot=lst_gene_tracks, 
                               lst_gene_hratios=lst_gene_hratios,
                               volcano_top_n=volcano_top_n)

    generate_plots(gene_result_path=gene_result_path,
                  pos_result_path=pos_result_path,
                  maf_path=maf_path,
                  miss_prob_path=miss_prob_path,
                  seq_df_path=seq_df_path,
                  cohort=cohort,
                  datasets_dir=datasets_dir,
                  annotations_dir=annotations_dir,
                  output_dir=output_dir,
                  plot_pars=plot_pars,
                  maf_path_for_nonmiss=maf_for_nonmiss_path,
                  c_genes_only=c_genes_only,
                  n_genes=max_n_genes,
                  lst_genes=genes,
                  save_plot=True,
                  show_plot=False,
                  save_csv=output_csv,
                  include_all_pos=output_all_pos,
                  title=cohort,
                  use_fdr=fdr)


# =============================================================================
#                              CHIMERAX PLOTS
# =============================================================================

@oncodrive3D.command(context_settings=dict(help_option_names=['-h', '--help']),
               help="Generate 3D plots using ChimeraX.")
@click.option("-o", "--output_dir", 
              help="Directory where to save the plots", type=str, required=True)
@click.option("-g", "--gene_result_path", 
              help="Path to genes-level O3D result", type=click.Path(exists=True), required=True)
@click.option("-p", "--pos_result_path", 
              help="Path to positions-level O3D result", type=click.Path(exists=True), required=True)
@click.option("-d", "--datasets_dir", 
              help="Path to datasets", type=click.Path(exists=True), required=True)
@click.option("-s", "--seq_df_path", 
              help="Path to sequences dataframe", type=click.Path(exists=True), required=True)
@click.option("-c", "--cohort", 
              help="Cohort name", default="")
@click.option("--max_n_genes", help="Maximum number of genes to plot", type=int, default=30)
@click.option("--pixel_size", help="Pixel size (smaller value is larger number of pixels)", type=float, default=0.08)
@click.option("--cluster_ext", help="Include extended clusters", is_flag=True)
@click.option("--fragmented_proteins", help="Include fragmented proteins", is_flag=True)
@click.option("--transparent_bg", help="Set background as transparent", type=str, is_flag=True)
@click.option("--chimerax_bin", help="Path to chimerax installation", type=str, default="/usr/bin/chimerax")
@click.option("-v", "--verbose", help="Verbose", is_flag=True)
@setup_logging_decorator
def chimerax_plot(output_dir,
                  gene_result_path,
                  pos_result_path,
                  datasets_dir,
                  seq_df_path,
                  cohort,
                  max_n_genes,
                  pixel_size,
                  cluster_ext,
                  fragmented_proteins,
                  transparent_bg,
                  chimerax_bin,
                  verbose):
    """"Generate images of structures annotated with clustering metrics."""

    from scripts.plotting.chimerax_plot import generate_chimerax_plot

    startup_message(__version__, "Starting plot generation..")
    logger.info(f"Output dir: {output_dir}")
    logger.info(f"Gene result path: {gene_result_path}")
    logger.info(f"Position result path: {pos_result_path}")
    logger.info(f"Datasets dir: {datasets_dir}")
    logger.info(f"Sequence dataframe path: {seq_df_path}")
    logger.info(f"Cohort: {cohort}")
    logger.info(f"Max number of genes to plot: {max_n_genes}")
    logger.info(f"Pixel size: {pixel_size}")
    logger.info(f"Cluster extended: {cluster_ext}")
    logger.info(f"Fragmented proteins: {fragmented_proteins}")
    logger.info(f"Transparent background: {transparent_bg}")
    logger.info(f"Verbose: {bool(verbose)}")
    logger.info(f'Log path: {os.path.join(output_dir, "log")}')
    logger.info("")

    generate_chimerax_plot(output_dir,
                        gene_result_path,
                        pos_result_path,
                        datasets_dir,
                        seq_df_path,
                        cohort,
                        max_n_genes,
                        pixel_size,
                        cluster_ext,
                        fragmented_proteins,
                        transparent_bg,
                        chimerax_bin)

if __name__ == "__main__":
    oncodrive3D()