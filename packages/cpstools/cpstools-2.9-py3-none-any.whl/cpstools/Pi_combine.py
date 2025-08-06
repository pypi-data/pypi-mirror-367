import argparse
import os
import subprocess
import sys
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Seq import MutableSeq


class CustomHelpFormatter(argparse.HelpFormatter):
    def format_help(self):
        help_text = super().format_help()
        description = """
        Calculate Pi valus from Genbank files and sort as cp order.
        Author: Xu wenbo
        Org:    China Pharmaceutical University
        Email:  xwb7533@163.com"""

        return f"{description}\n\n{help_text}"


def IGS_extract(input_file, fasta_dir, info_dir):
    # 正确处理包含多个'.'的文件名 (例如 'species.name.v1.gb')
    base_name = os.path.basename(input_file)
    if '.' in base_name:
        base_name = base_name.rsplit('.', 1)[0] # 从右边分割一次，保留前面的部分

    try:
        # 使用 with 语句自动管理文件，更安全
        for rec in SeqIO.parse(input_file, format='genbank'):
            genome_length = len(rec.seq)
            my_seq = rec.seq
            
            all_feature = []
            for feature in rec.features:
                if feature.type in ['CDS', 'tRNA', 'rRNA'] and 'gene' in feature.qualifiers:
                    all_feature.append(feature)
            
            # 按起始位置排序，确保基因顺序正确
            all_feature.sort(key=lambda f: f.location.start)

            all_info = []
            # 遍历排序后的特征列表
            for i in range(len(all_feature)):
                try:
                    # ==================== 错误修正 ====================
                    # 必须使用 all_feature[i] 来获取当前循环的特征对象
                    current_feature = all_feature[i] 
                    gene_name = current_feature.qualifiers['gene'][0].replace(" ", "_").replace("/", "_")
                    gene_location = current_feature.location.parts
                    # ================================================

                    gene1_exon_info = [[int(part.start), int(part.end), part.strand] for part in gene_location]
                    exon_number = len(gene_location)
                    
                    if exon_number == 1:
                        all_info.append(
                            f"{gene_name}\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                    elif exon_number == 2:
                        # 跨越原点的基因处理
                        if gene1_exon_info[0][1] > gene1_exon_info[1][0] and gene1_exon_info[0][0] > 0: # 假设跨越原点
                            all_info.append(
                                f"{gene_name}\t{gene1_exon_info[0][0]}\t{genome_length}\t0\t{gene1_exon_info[1][1]}\t{gene1_exon_info[0][2]}")
                        else: # 普通的两个外显子
                            all_info.append(
                                f"{gene_name}_1\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                            all_info.append(
                                f"{gene_name}_2\t{gene1_exon_info[1][0]}\t{gene1_exon_info[1][1]}\t{gene1_exon_info[1][2]}")
                    elif exon_number >= 3:
                        for idx, exon_info in enumerate(gene1_exon_info, 1):
                            all_info.append(f"{gene_name}_{idx}\t{exon_info[0]}\t{exon_info[1]}\t{exon_info[2]}")

                except (KeyError, IndexError) as e:
                    # 如果某个 feature 缺少 'gene' 标签，跳过它并继续
                    print(f"Skipping a feature in {base_name} due to missing data: {e}")
                    continue
            
            # 按起始位置排序信息列表
            all_info = sorted(list(set(all_info)), key=lambda x: int(x.split('\t')[1]))
            
            save_file = os.path.join(info_dir, f'{base_name}_intergenic_location.txt')
            
            with open(save_file, 'w') as save_file_w:
                if len(all_info) > 1:
                    for i in range(len(all_info) - 1):
                        info_list = all_info[i].split('\t')
                        next_list = all_info[i+1].split('\t')
                        # info_list[-2] 是倒数第二个元素，即end_position
                        # next_list[1] 是第二个元素，即start_position
                        save_file_w.write(f"{info_list[0]}-{next_list[0]}\t{info_list[-2]}\t{next_list[1]}\n")
                
                # 处理环状基因组的首尾相接部分
                if len(all_info) > 0:
                    end_gene_info = all_info[-1].split('\t')
                    start_gene_info = all_info[0].split('\t')
                    
                    # 最后一个基因的结束位置
                    last_gene_end = int(end_gene_info[-2])
                    # 第一个基因的开始位置
                    first_gene_start = int(start_gene_info[1])

                    if last_gene_end < first_gene_start:
                        # 正常环状，没有跨越原点的基因
                        save_file_w.write(f"{end_gene_info[0]}-{start_gene_info[0]}\t{last_gene_end}\t{first_gene_start}\n")
                    # 如果最后一个基因已经跨越了原点，它的信息可能已经是多段式的，这种情况比较复杂，暂时按原逻辑处理
                    elif int(end_gene_info[2]) < genome_length:
                         save_file_w.write(f"{end_gene_info[0]}-{start_gene_info[0]}\t{last_gene_end}\t{genome_length}\t0\t{first_gene_start}\n")

            all_fasta_file = os.path.join(fasta_dir, f'{base_name}_IGS.fasta')
            
            with open(all_fasta_file, 'w') as all_fasta, open(save_file, 'r') as save_results:
                for line in save_results:
                    parts = line.strip().split('\t')
                    header = parts[0].replace(" ", "_").replace("/", "_")
                    if len(parts) == 3:
                        start, end = int(parts[1]), int(parts[2])
                        if end > start:
                            all_fasta.write(f">{header}\n{my_seq[start:end]}\n")
                    elif len(parts) == 5:
                        start1, end1 = int(parts[1]), int(parts[2])
                        start2, end2 = int(parts[3]), int(parts[4])
                        all_fasta.write(f">{header}\n{my_seq[start1:end1]}{my_seq[start2:end2]}\n")

    except Exception as e:
        print(f"FATAL: Error processing file {input_file}: {e}")
        

def common_gene_extract(input_dir):
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"The input directory {input_dir} does not exist.")

    gb_files = [f for f in os.listdir(input_dir) if f.endswith(('.gb', '.gbk'))]
    if not gb_files:
        raise FileNotFoundError("No GenBank files (.gb, .gbk) found in the input directory.")

    work_dir = os.path.dirname(input_dir)
    
    reference_file = os.path.join(input_dir, gb_files[0])
    all_gene_set = set()
    for rec in SeqIO.parse(reference_file, 'genbank'):
        for feature in rec.features:
            if feature.type in ['CDS', 'tRNA', 'rRNA'] and 'gene' in feature.qualifiers:
                all_gene_set.add(feature.qualifiers['gene'][0])

    for file in gb_files[1:]:
        single_gene_set = set()
        gb_file = os.path.join(input_dir, file)
        for rec in SeqIO.parse(gb_file, 'genbank'):
            for feature in rec.features:
                if feature.type in ['CDS', 'tRNA', 'rRNA'] and 'gene' in feature.qualifiers:
                    single_gene_set.add(feature.qualifiers['gene'][0])
        all_gene_set_lower = {g.lower() for g in all_gene_set}
        single_gene_set_lower = {g.lower() for g in single_gene_set}
        common_lower = all_gene_set_lower.intersection(single_gene_set_lower)
        all_gene_set = {g for g in all_gene_set if g.lower() in common_lower}
    
    all_gene = sorted(list(all_gene_set))
    
    gene_name_file = os.path.join(work_dir, 'gene_cp_sort.txt')
    with open(gene_name_file, 'w') as f:
        for gene in all_gene:
            f.write(f"{gene}\n")

    save_dir = os.path.join(work_dir, 'common_gene')
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"Found {len(all_gene)} common genes. Unaligned files saved to:\n\t\t\t{save_dir}")

    for gene_name in all_gene:
        file_name = f"{gene_name.replace('/', '_')}.fasta"
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'w') as fasta_file:
            for gb_file_name in gb_files:
                base_name = os.path.splitext(gb_file_name)[0]
                fasta_file.write(f">{base_name}\n")
                
                gb_file_path = os.path.join(input_dir, gb_file_name)
                for rec in SeqIO.parse(gb_file_path, 'genbank'):
                    my_seqs = []
                    for feature in rec.features:
                        if feature.type in ['CDS', 'tRNA', 'rRNA'] and 'gene' in feature.qualifiers:
                            if feature.qualifiers['gene'][0].lower() == gene_name.lower():
                                my_seqs.append(feature.extract(rec.seq))
                    if my_seqs:
                        longest_seq = max(my_seqs, key=len)
                        fasta_file.write(f"{longest_seq}\n")
    
    return save_dir, gene_name_file

def common_IGS(input_dir):
    all_common_ids = []
    fasta_files = [f for f in os.listdir(input_dir) if f.endswith('.fasta')]
    
    if not fasta_files:
        print("No .fasta files found in the IGS directory.")
        return None, None

    reference_file = os.path.join(input_dir, fasta_files[0])
    with open(reference_file, 'r') as f:
        all_common_ids = [rec.id for rec in SeqIO.parse(f, 'fasta')]

    for fasta_file in fasta_files[1:]:
        current_ids = {rec.id for rec in SeqIO.parse(os.path.join(input_dir, fasta_file), 'fasta')}
        current_ids_lower = {x.lower() for x in current_ids}
        all_common_ids = [cid for cid in all_common_ids if cid.lower() in current_ids_lower]

    work_dir = os.path.dirname(input_dir)
    igs_order_file = os.path.join(work_dir, 'IGS', 'cp_sort_IGS.txt')
    os.makedirs(os.path.dirname(igs_order_file), exist_ok=True)
    with open(igs_order_file, 'w') as f:
        for i in all_common_ids:
            f.write(f"{i}\n")

    save_dir = os.path.join(work_dir, 'unalign_common_IGS')
    os.makedirs(save_dir, exist_ok=True)
    
    print(f"Found {len(all_common_ids)} common intergenic spacers. Unaligned files saved to:\n\t{save_dir}")

    for common_name in all_common_ids:
        save_file_path = os.path.join(save_dir, f"{common_name}.fasta")
        with open(save_file_path, 'w') as save_file:
            for fasta_file in fasta_files:
                fasta_path = os.path.join(input_dir, fasta_file)
                species_name = os.path.splitext(os.path.basename(fasta_file))[0].replace('_IGS', '')
                for rec in SeqIO.parse(fasta_path, format='fasta'):
                    if rec.id.lower() == common_name.lower():
                        save_file.write(f">{species_name}\n{rec.seq}\n")
    
    return save_dir, igs_order_file

def is_mafft_available():
    try:
        subprocess.run(["mafft", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def multi_mafft(input_dir, mafft_path=None):
    if not input_dir or not os.path.exists(input_dir):
        print(f"Skipping alignment: input directory does not exist or is empty: {input_dir}")
        return None

    parent_dir = os.path.dirname(input_dir)
    align_dir_name = 'align_gene' if "gene" in os.path.basename(input_dir) else 'align_IGS'
    align_dir = os.path.join(parent_dir, align_dir_name)
    os.makedirs(align_dir, exist_ok=True)

    mafft_executable = mafft_path if mafft_path else 'mafft'
    files_to_align = [f for f in os.listdir(input_dir) if f.endswith('.fasta')]
    if not files_to_align:
        print(f"No '.fasta' files to align in {os.path.basename(input_dir)}.")
        return align_dir
    
    print(f"Aligning {len(files_to_align)} files in {os.path.basename(input_dir)}...")
    for file in files_to_align:
        input_file = os.path.join(input_dir, file)
        output_file = os.path.join(align_dir, file)
        command = f'"{mafft_executable}" --auto "{input_file}" > "{output_file}"'
        subprocess.run(command, shell=True, check=True, capture_output=True)
    return align_dir

def calculate_pi_for_directory(work_dir):
    if not work_dir or not os.path.exists(work_dir):
        print(f"Skipping Pi calculation: directory not found: {work_dir}")
        return None

    all_pi_results = []
    for align_fasta in os.listdir(work_dir):
        if not align_fasta.endswith('.fasta'): continue
        
        fasta_file = os.path.join(work_dir, align_fasta)
        records = list(SeqIO.parse(fasta_file, 'fasta'))
        if len(records) < 2: continue

        num_seqs = len(records)
        seq_len = len(records[0].seq)
        
        ungapped_cols = [i for i in range(seq_len) if '-' not in "".join(rec.seq[i] for rec in records)]

        if not ungapped_cols:
            final_pi = 0.0
        else:
            num_sites = len(ungapped_cols)
            pairwise_diffs = 0
            num_comparisons = num_seqs * (num_seqs - 1) / 2
            
            for i in range(num_seqs):
                for j in range(i + 1, num_seqs):
                    seq1 = records[i].seq
                    seq2 = records[j].seq
                    diffs = sum(1 for k in ungapped_cols if seq1[k] != seq2[k])
                    pairwise_diffs += diffs
            
            pi = pairwise_diffs / num_comparisons
            final_pi = pi / num_sites if num_sites > 0 else 0.0

        region_name = os.path.splitext(align_fasta)[0]
        all_pi_results.append(f"{region_name}\t{final_pi:.5f}")
    
    pi_results_file = os.path.join(os.path.dirname(work_dir), f'Pi_results_{os.path.basename(work_dir)}.txt')
    with open(pi_results_file, 'w') as ff:
        for each_pi in sorted(all_pi_results):
            ff.write(f"{each_pi}\n")
    return pi_results_file

def sort_pi_file(pi_file, order_file, output_filename):
    if not pi_file or not order_file: return None
    pi_dict = {line.strip().split('\t')[0].lower(): line.strip().split('\t')[1] for line in open(pi_file, 'r')}
    
    output_path = os.path.join(os.path.dirname(pi_file), output_filename)
    with open(order_file, 'r') as f_order, open(output_path, 'w') as f_out:
        for line in f_order:
            name = line.strip()
            pi_value = pi_dict.get(name.lower(), "N/A") 
            f_out.write(f"{name}\t{pi_value}\n")
    return output_path


# ==============================================================================
# MAIN CALLABLE FUNCTION
# This is the function you will import and call from your CPStools main script.
# ==============================================================================

def calculate_pi(args):
    """
    Main workflow for calculating Pi values for genes and IGS regions.
    This function can be called from other scripts.
    'args' should be an object with 'work_dir' and 'mafft_path' attributes.
    """
    work_dir = os.path.abspath(args.work_dir)
    parent_dir = os.path.dirname(work_dir)

    print("--- Step 1: Extracting Common Genes ---")
    common_gene_dir, gene_order_file = common_gene_extract(work_dir)
    print('-' * 80)

    print("--- Step 2: Extracting IGS Regions ---")
    fasta_dir = os.path.join(parent_dir, 'IGS')
    info_dir = os.path.join(parent_dir, 'info')
    os.makedirs(fasta_dir, exist_ok=True)
    os.makedirs(info_dir, exist_ok=True)

    gb_files = [f for f in os.listdir(work_dir) if f.endswith(('.gb', '.gbk'))]
    print(f"Processing {len(gb_files)} GenBank files...")
    for file in gb_files:
        file_path = os.path.join(work_dir, file)
        IGS_extract(file_path, fasta_dir, info_dir)
    print("IGS extraction complete.")
    print('-' * 80)

    print("--- Step 3: Finding Common IGS ---")
    common_igs_dir, igs_order_file = common_IGS(fasta_dir)
    print('-' * 80)
    
    if not (is_mafft_available() or args.mafft_path):
        print("MAFFT not found. Skipping alignment and Pi calculation.")
        print("Please install MAFFT, add to PATH, or provide its path with --mafft_path.")
        sys.exit(1)
        
    print("--- Step 4: Aligning Sequences ---")
    align_gene_dir = multi_mafft(common_gene_dir, args.mafft_path)
    if align_gene_dir: print(f'Aligned Gene sequences saved at: {align_gene_dir}')
    
    align_igs_dir = multi_mafft(common_igs_dir, args.mafft_path)
    if align_igs_dir: print(f'Aligned IGS sequences saved at: {align_igs_dir}')
    print('-' * 80)
    
    print("--- Step 5: Calculating Pi Values ---")
    gene_pi_file = calculate_pi_for_directory(align_gene_dir)
    if gene_pi_file: print(f"Raw Pi values for Genes saved at: {gene_pi_file}")
    
    igs_pi_file = calculate_pi_for_directory(align_igs_dir)
    if igs_pi_file: print(f"Raw Pi values for IGS saved at: {igs_pi_file}")
    print('-' * 80)
    
    print("--- Step 6: Sorting Pi Values by Genome Order ---")
    final_gene_pi_sorted = sort_pi_file(gene_pi_file, gene_order_file, 'gene_sort_as_cp_order.txt')
    final_igs_pi_sorted = sort_pi_file(igs_pi_file, igs_order_file, 'IGS_sort_as_cp_order.txt')
    
    print("\n" + "="*25 + " PIPELINE FINISHED " + "="*25)
    if final_gene_pi_sorted: print(f"Sorted Gene Pi values are in: {final_gene_pi_sorted}")
    if final_igs_pi_sorted: print(f"Sorted IGS Pi values are in: {final_igs_pi_sorted}")
    print("=" * 70)

# ==============================================================================
# Code for running this script directly from the command line
# ==============================================================================

def main():
    """
    Parses command line arguments and calls the main workflow.
    """
    parser = argparse.ArgumentParser(
        description="Calculate Pi values from Genbank files for genes and IGS regions, and sort by genome order."
    )
    parser.add_argument("-d", "--work_dir", required=True, help="Input directory of genbank files")
    parser.add_argument("-m", "--mafft_path", help="Path to MAFFT executable if not in environment path")
    
    args = parser.parse_args()
    
    # Call the main, importable function
    calculate_pi(args)

if __name__ == "__main__":
    main()