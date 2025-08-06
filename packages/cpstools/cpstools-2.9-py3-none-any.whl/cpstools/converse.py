import argparse
import os
import sys
from Bio import SeqIO
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio.SeqRecord import SeqRecord

# ==============================================================================
# Help Formatter
# ==============================================================================

class CustomHelpFormatter(argparse.HelpFormatter):
    def format_help(self):
        help_text = super().format_help()
        description = """
        Converse sequence annotation files between different formats.
        Author: Xu wenbo
        Org:    China Pharmaceutical University
        Email:  xwb7533@163.com"""
        return f"{description}\n\n{help_text}"

# ==============================================================================
# Helper & Core Conversion Functions
# ==============================================================================

def parse_genbank_file(input_file):
    """Safely parse a GenBank file and return a list of SeqRecord objects."""
    try:
        with open(input_file, 'r') as f:
            records = list(SeqIO.parse(f, 'genbank'))
            if records:
                return records
            else:
                print(f"Warning: No valid GenBank records found in {input_file}")
                return None
    except Exception as e:
        print(f"Error: Failed to parse GenBank file '{input_file}': {e}")
        return None

def gb2fa(input_file, save_file):
    """Converts a GenBank file to a FASTA file."""
    records = parse_genbank_file(input_file)
    if not records:
        return # Stop if parsing failed

    # Use the filename (without extension) as the FASTA header ID
    seq_id = os.path.splitext(os.path.basename(input_file))[0]
    
    with open(save_file, 'w') as ff:
        for rec in records:
            # Override the record's ID with the filename for consistency
            ff.write(f'>{seq_id}\n{rec.seq}\n')

def gb2mVISTA(input_file, save_file):
    """Converts a GenBank file to mVISTA format."""
    records = parse_genbank_file(input_file)
    if not records:
        return

    all_info = []
    # Process only the first record, typical for chloroplast genomes
    rec = records[0] 
    
    for feature in rec.features:
        gene_name = feature.qualifiers.get('gene', [None])[0]
        if not gene_name: continue

        # Standardize feature type for mVISTA
        if feature.type == 'CDS':
            vista_type = 'exon'
        elif feature.type in ['tRNA', 'rRNA']:
            vista_type = 'utr'
        else:
            continue
        
        for part in feature.location.parts:
            # Biopython uses 0-based indexing, mVISTA is 1-based
            start, end = int(part.start) + 1, int(part.end)
            strand_char = '<' if part.strand == -1 else '>'
            
            # Add gene info first, then exon/utr info
            all_info.append(f"{strand_char} {start} {end} {gene_name}")
            all_info.append(f"{start} {end} {vista_type}")

    # Remove duplicates while preserving order
    unique_info = sorted(list(set(all_info)), key=lambda x: int(x.split()[1]))

    with open(save_file, 'w') as ff:
        for line in unique_info:
            ff.write(f"{line}\n")

def gb2tbl(input_file, save_file):
    """Converts a GenBank file to a TBL file."""
    records = parse_genbank_file(input_file)
    if not records:
        return

    output_order = ["trans_splicing", "exception", "pseudo", "codon_start", "product", "gene", "transl_table"]
    
    with open(save_file, 'w') as ff:
        for rec in records:
            ff.write(f">Feature {rec.id}\n")
            # Skip the 'source' feature
            for feature in rec.features:
                if feature.type == 'source':
                    continue
                
                # Write location lines
                loc_lines = []
                for part in feature.location.parts:
                    start, end = (part.end, part.start + 1) if part.strand == -1 else (part.start + 1, part.end)
                    loc_lines.append(f"{start}\t{end}")
                
                ff.write(f"{loc_lines[0]}\t{feature.type}\n")
                for line in loc_lines[1:]:
                    ff.write(f"{line}\n")

                # Write qualifier lines
                for key in output_order:
                    if key in feature.qualifiers:
                        value = feature.qualifiers[key][0]
                        ff.write(f"\t\t\t{key}\t{value}\n")

# --- NEW FUNCTION FOR GE2GB ---
def ge2gb(input_file, output_file):
    """
    Converts a Geneious-annotated GenBank file to a standard, clean GenBank file.
    - Sorts features by location.
    - Filters qualifiers to a standard set.
    - Adds translation to CDS if missing.
    """
    sort_order = {'gene': 0, 'CDS': 1, 'tRNA': 2, 'rRNA': 3}
    keys_to_keep = ['gene', 'product', 'exception', 'transl_table', 'codon_start', 
                    'pseudo', 'trans_splicing', 'translation', 'organism', 'organelle', 'mol_type']
    
    try:
        records_to_write = []
        for rec in SeqIO.parse(input_file, 'gb'):
            # Separate source feature from others
            source_feature = next((f for f in rec.features if f.type == 'source'), None)
            other_features = [f for f in rec.features if f.type != 'source']

            # Sort other features by start position and then type
            sorted_features = sorted(other_features,
                                     key=lambda f: (int(f.location.start), sort_order.get(f.type, 4)))

            processed_features = []
            # Process source feature first if it exists
            if source_feature:
                source_qualifiers = {k: v for k, v in source_feature.qualifiers.items() if k in keys_to_keep}
                processed_features.append(SeqFeature(location=source_feature.location, type='source', qualifiers=source_qualifiers))

            # Process the sorted features
            for feature in sorted_features:
                filtered_qualifiers = {k: v for k, v in feature.qualifiers.items() if k in keys_to_keep}
                
                # Add translation if CDS and missing
                if feature.type == 'CDS' and 'translation' not in filtered_qualifiers:
                    try:
                        table = int(filtered_qualifiers.get('transl_table', [11])[0])
                        translation = feature.extract(rec.seq).translate(table=table, cds=True, stop_symbol="")
                        filtered_qualifiers['translation'] = [str(translation)]
                    except Exception as e:
                        print(f"Warning: Could not translate {filtered_qualifiers.get('gene', ['N/A'])[0]} in {rec.id}: {e}")

                processed_features.append(SeqFeature(location=feature.location, type=feature.type, qualifiers=filtered_qualifiers))
            
            new_rec = SeqRecord(rec.seq, id=rec.id, name=rec.name, description=rec.description,
                                annotations=rec.annotations, features=processed_features)
            records_to_write.append(new_rec)
        
        with open(output_file, 'w') as out_handle:
            SeqIO.write(records_to_write, out_handle, 'genbank')
            
    except Exception as e:
        print(f"Error processing {input_file} for ge2gb conversion: {e}")


# ==============================================================================
# Main Dispatcher Function
# ==============================================================================

def converse_format(args):
    """Main function to handle file conversion based on user arguments."""
    mode = args.mode
    input_path = args.input_dir

    # 1. 将输入路径转为绝对路径，以处理 './' 或 '../' 等相对路径
    abs_input_path = os.path.abspath(input_path)

    # 2. 检查路径是否存在
    if not os.path.exists(abs_input_path):
        print(f"Error: Input path '{input_path}' does not exist.")
        sys.exit(1)

    # 3. 确定输入的基本目录 (无论是文件还是文件夹，我们都找到它所在的目录)
    #    并获取所有待处理的文件列表
    if os.path.isdir(abs_input_path):
        # 如果输入是目录, 它本身就是基本目录
        input_base_dir = abs_input_path
        input_files = [os.path.join(input_base_dir, f) for f in os.listdir(input_base_dir)]
    elif os.path.isfile(abs_input_path):
        # 如果输入是文件, 它的基本目录是它所在的文件夹
        input_base_dir = os.path.dirname(abs_input_path)
        input_files = [abs_input_path] # 文件列表只包含它自己
    else:
        print(f"Error: Input path '{input_path}' is not a valid file or directory.")
        sys.exit(1)
        
    # 4. 【核心步骤】获取输入基本目录的 "父目录"
    #    例如, 如果输入是 /path/to/gb_files, 这里会得到 /path/to/
    output_parent_dir = os.path.dirname(input_base_dir)

    # 5. 在父目录中创建最终的输出文件夹
    #    例如, os.path.join('/path/to/', 'fasta') -> '/path/to/fasta'
    output_dir = os.path.join(output_parent_dir, mode)

    # 6. 创建输出目录（如果不存在）
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    else:
        print(f"Warning: Output directory '{output_dir}' already exists. Files may be overwritten.")
        
    print(f"\n--- Starting conversion to '{mode}' mode ---")
    
    # 后面是你已有的转换逻辑，无需修改
    conversion_map = {
        'fasta': ('.fasta', gb2fa),
        'mVISTA': ('.mVISTA', gb2mVISTA),
        'tbl': ('.tbl', gb2tbl),
        'ge2gb': ('.gb', ge2gb)
    }

    if mode not in conversion_map:
        print(f"Error: Invalid mode '{mode}'.")
        return

    output_ext, conversion_func = conversion_map[mode]

    processed_count = 0
    for file_path in input_files:
        if file_path.lower().endswith(('.gb', '.gbk')):
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            # 这行代码现在会使用我们正确计算出的 output_dir
            save_file = os.path.join(output_dir, base_name + output_ext)
            
            print(f"Converting '{os.path.basename(file_path)}' -> '{os.path.relpath(save_file)}'")
            conversion_func(file_path, save_file)
            processed_count += 1
        else:
            if os.path.isdir(abs_input_path):
                print(f"Skipping non-GenBank file: {os.path.basename(file_path)}")

    print(f"\n--- Conversion complete. Processed {processed_count} files. ---")
    print(f"Results are saved in: {os.path.abspath(output_dir)}")

# ==============================================================================
# Command-Line Interface
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Converts sequence annotation files between different formats.",
        formatter_class=CustomHelpFormatter
    )
    parser.add_argument("-d", "--input_dir", help="Input directory or a single GenBank file.", required=True)
    # UPDATED: Added 'ge2gb' to choices and help text
    parser.add_argument(
        "-m", "--mode", 
        choices=['fasta', 'mVISTA', 'tbl', 'ge2gb'],
        required=True,
        help="Conversion mode:\n"
             "'fasta': GenBank to FASTA.\n"
             "'mVISTA': GenBank to mVISTA.\n"
             "'tbl': GenBank to Sequin Table (TBL).\n"
             "'ge2gb': Clean up Geneious-annotated GenBank to standard GenBank."
    )
    
    args = parser.parse_args()
    converse_format(args) # Call the main dispatcher function

if __name__ == "__main__":
    main()