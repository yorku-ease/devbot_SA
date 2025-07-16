"""
Evaluates LLM-generated PlantUML diagrams.
"""


from argparse import ArgumentParser
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .diff import comp_puml_metrics


def save_heatmap(df: pd.DataFrame, name: str) -> None:
    """
    Saves data frames as heatmaps.

    Args:
        df: Data frame to save as heatmap.
        name: Name of heatmap.
    """
    plt.imshow(df.values, cmap='viridis', aspect='auto')
    plt.colorbar()

    plt.xticks(ticks=range(len(df.columns)), labels=df.columns, rotation=90)
    plt.yticks(ticks=range(len(df.index)), labels=df.index)

    for i in range(df.shape[0]):
        for j in range(df.shape[1]):
            value = df.iat[i, j]
            plt.text(j, i, str(round(value, 3)), ha='center', va='center', color='white')

    plt.savefig(name, bbox_inches='tight')
    plt.close()


def eval_folder(folder: Path) -> pd.DataFrame:
    """
    Evaluates folders of LLM-generated PlantUML diagrams.

    Args:
        folder: Folder containing LLM-generated PlantUML diagrams
            and the ground truth Benchmark.puml.

    Returns:
        Data frame containing various metrics for each LLM-generated diagram.
    """
    df = pd.DataFrame(columns=['Distance', 'TPs', 'FPs', 'FNs',
                               'Precision', 'Recall', 'F1'])

    for file in Path(folder).glob('*.puml'):
        if file.name != 'Benchmark.puml':
            df.loc[file.stem] = comp_puml_metrics(str(folder.joinpath('Benchmark.puml')),
                                                  str(file))

    return df


def main(folder: Path) -> None:
    if all(map(lambda x: x.is_file(), folder.iterdir())):
        df = eval_folder(folder)
        df.to_csv('eval.csv')

    elif all(map(lambda x: x.is_dir(), folder.iterdir())):
        dist_df = pd.DataFrame()
        prec_df = pd.DataFrame()
        recall_df = pd.DataFrame()
        f1_df = pd.DataFrame()

        for sub in folder.iterdir():
            df = eval_folder(sub)
            for first_model in df.index:
                dist_df.loc[first_model, sub.name] = df.loc[first_model, 'Distance']
                prec_df.loc[first_model, sub.name] = df.loc[first_model, 'Precision']
                recall_df.loc[first_model, sub.name] = df.loc[first_model, 'Recall']
                f1_df.loc[first_model, sub.name] = df.loc[first_model, 'F1']

        save_heatmap(dist_df, f'dist.svg')
        save_heatmap(prec_df, f'prec.svg')
        save_heatmap(recall_df, f'recall.svg')
        save_heatmap(f1_df, f'f1.svg')

    else:
        raise RuntimeError('Folder must exclusively contain either files or other folders.')


if __name__ == '__main__':
    parser = ArgumentParser(description='Evaluates LLM-generated PlantUML diagrams.')
    parser.add_argument('folder',
                        type=str,
                        help='Folder containing either: \
                              I) LLM-generated PlantUML diagrams and the ground truth Benchmark.puml, or\
                              II) Folders each containing LLM-generated PlantUML diagrams and the ground truth Benchmark.puml.\
                              If the latter, iterative refinement is assumed; that is, each folder represents the second model,\
                              with the first model denoted by the files therein.\
                              For example, o3/Gemini.puml means Gemini was the first model and o3 the second.')
    args = parser.parse_args()

    main(Path(args.folder))
