import sys
import json
import argparse

import evaluate
import pandas as pd
import numpy as np

from sectiontagger import SectionTagger
section_tagger = SectionTagger()


SECTION_DIVISIONS = ['subjective', 'objective_exam', 'objective_results', 'assessment_and_plan']

TASKA_RANGE = [0,199]
TASKA_PREFIX = ''

TASKB_RANGE = [88,127]
TASKB_PREFIX = 'D2N'

TASKC_RANGE = [128,167]
TASKC_PREFIX = 'D2N'


def add_section_divisions(row, dialogue_column ):
    row['src_len'] = len(row[ dialogue_column ].split())
    for evaltype in ['reference', 'prediction']:
        text = row[evaltype]
        text_with_endlines = text.replace( '__lf1__', '\n' )
        detected_divisions = section_tagger.divide_note_by_metasections(text_with_endlines)
        for detected_division in detected_divisions:
            label, _, _, start, _, end = detected_division
            row[ '%s_%s' % (evaltype, label)] = text_with_endlines[start:end].replace('\n', '__lf1__')

    return row


def select_values_by_indices(lst, indices) :
    return [lst[ind] for ind in indices]


def read_text(fn):
    with open(fn, 'r') as f:
        texts = f.readlines()
    return texts


def _validate(args, df_predictions, task_prefix, task_range):
    id_range = df_predictions.apply(lambda row: int( str(row[args.id_column]).replace(task_prefix, '')), axis=1)
    min_id = min(id_range)
    max_id = max(id_range)
    if min_id < task_range[0] or min_id > task_range[1]:
        print('Your encounter ID range does not match the test encounters')
        sys.exit(1)
    if max_id < task_range[0] or max_id > task_range[1]:
        print('Your encounter ID range does not match the test encounters')
        sys.exit(1)
    if not args.debug and len(df_predictions) != task_range[1] - task_range[0] + 1:
        print('The number of test encounters does not match expected for this task!')
        sys.exit(1)


def test_id_range( args, df_predictions):
    # Make sure args.id_column is in range expected by task prefix (taskA or taskB)
    print( df_predictions.columns )
    id_1 = '%s' %df_predictions.iloc[0][args.id_column]
    if args.task == 'taskA' and TASKA_PREFIX in id_1:
        if args.task == 'taskB':
            print('Your ID prefixes do not match this tasks expected encounter_ids.')
            sys.exit(1)
        _validate(args, df_predictions, TASKA_PREFIX, TASKA_RANGE)
    elif TASKB_PREFIX in id_1:
        if args.task == 'taskA':
            print( 'Your ID prefixes do not match this tasks expected encounter_ids.' )
            sys.exit(1)
        if args.task == 'taskB':
            _validate(args, df_predictions, TASKB_PREFIX, TASKB_RANGE)
        if args.task == 'taskC':
            _validate(args, df_predictions, TASKC_PREFIX, TASKC_RANGE)
    else:
        print(f'Your encounter ID -> {id_1} does not have an identifiable prefix supported by this evaluation' )
        sys.exit(1)


def filter_and_aggregate(obj, indices):
    agg_obj = {}
    for k, v in obj.items():
        agg_obj[k] = float(np.mean([v[i] for i in indices]))
    return agg_obj


if __name__ == "__main__" :
    parser = argparse.ArgumentParser(
        prog='evaluate_summarization',
        description='This runs basic evaluation for both snippet (taskA) and full note summarization (taskB).'
    )
    parser.add_argument('--fn_gold', required=True, help='filename of gold references requires id and note column.')
    parser.add_argument('--fn_sys', required=True, help='filename of system references requires id and note column.')
    parser.add_argument(
        '--metadata_file', dest='fn_metadata', action='store', default=None,
        help='filename of metadata requires id and dataset column.'
    )
    parser.add_argument(
        '--task', action='store', default='taskB',
        help='summarization task, default is for full note (taskB). (use snippet, taskA, otherwise).'
    )
    parser.add_argument('--id_column', default='TestID', help='column to use for identifying id.')
    parser.add_argument('--note_column', default='SystemOutput', help='column to use for identifying note.')
    parser.add_argument('--dialogue_column', default='dialogue', help='column to use for identifying dialogue.')
    parser.add_argument(
        '--use_section_check', action='store_true', default=False,
        help='this flag with make sure evaluation shuts down for full task if 0 section divisions are detected.'
    )
    parser.add_argument(
        '--note_length_cutoff', default=512, type=int,
        help='Consider less than note_length_cutoff to be short and vice-versa for long'
    )
    parser.add_argument('--experiment', default='default', help='Prefix for save file.')
    parser.add_argument('-debug', default=False, action='store_true', help='If true, just runs eval over first example')

    args = parser.parse_args()

    # Read in reference/hyp files -added the latin encoding as one of the participants' file had a strange character somewhere
    #df_references = pd.read_csv(args.fn_gold, encoding='latin1')
    #df_predictions = pd.read_csv(args.fn_sys, encoding='latin1')
    df_references = pd.read_csv(args.fn_gold)
    df_predictions = pd.read_csv(args.fn_sys)

    print(f'Gold path: {args.fn_gold} ({len(df_references)} summaries)')
    print(f'System path: {args.fn_sys} ({len(df_predictions)} summaries)')

    # Check id formatting to determine if something obvious is amiss based on encounter id's and task
    test_id_range(args, df_predictions)

    # read in metadata file - if none exists, just creates a dummy
    if args.fn_metadata is not None:
        full_df = pd.read_csv(args.fn_metadata)
        full_df = full_df.merge(df_references.rename({args.note_column: 'reference'}), on=args.id_column)
        full_df = full_df.merge(df_predictions.rename({args.note_column: 'prediction'}), on=args.id_column)
    else:
        def _conditional_rename(tmp_df, old_col, new_col):
            if new_col not in tmp_df.columns:
                tmp_df.rename(columns={old_col: new_col}, inplace=True)
        _conditional_rename(df_predictions, args.note_column, 'prediction')
        _conditional_rename(df_references, args.note_column, 'reference')
        # Only need id and prediction from df_predictions
        full_df = df_references.merge(df_predictions[[args.id_column, 'prediction']], on=args.id_column)
        full_df['dataset'] = 0

    # create lists for references/predictions so we only need to calculate the scores once per instance
    references = full_df['reference'].tolist()
    predictions = full_df['prediction'].tolist()
    num_test = len(full_df)

    # =========== ADD SECTION DIVISIONS IF THIS IS THE FULL ENCOUNTER TASK ==========
    if args.task == 'taskB':
        full_df = full_df.apply( lambda row: add_section_divisions( row, args.dialogue_column ), axis=1)
        print( full_df.columns )

        # ===========CHECKS TO MAKE SURE THERE ARE SECTIONS ==========
        #total_detected_sections = sum([
        #    full_df[f'prediction_{division}'].notna().sum() for division in SECTION_DIVISIONS
        #])
        #if total_detected_sections == 0:
        #    print('We detected 0 sections! - you can use override_section_check flag to run while ignoring this.')
        #    if args.use_section_check :
        #        sys.exit(1)

        # Fill in missing section divisions as empty string
        full_df.fillna('#####EMPTY#####', inplace=True)

        ######## ADD INSTANCES FOR SECTION DIVISION ########
        for division in SECTION_DIVISIONS:
            null_default = [''] * num_test
            references.extend(full_df.get(f'reference_{division}', null_default))
            predictions.extend(full_df.get(f'prediction_{division}', null_default))

        # sanity check, we should now have 5 x the original set (one for full note, 4 for the divisions)
        rn = len(references)
        pn = len(predictions)
        en = len(full_df) * 5
        assert rn == pn == en, f'The number of references ({rn}) and predictions ({pn}) does not match expected ({en})'

    ######## Load Metrics from HuggingFace ########
    print('Loading ROUGE, BERTScore, BLEURT from HuggingFace')
    scorers = {
        'rouge': (
            evaluate.load('rouge'),
            {'use_aggregator': False},
            ['rouge1', 'rouge2', 'rougeL', 'rougeLsum'],
            ['rouge1', 'rouge2', 'rougeL', 'rougeLsum']
        ),
        'bert_scorer': (
            evaluate.load('bertscore', device='cpu'),
            {'model_type': 'microsoft/deberta-xlarge-mnli', 'device':'cpu'},
            ['precision', 'recall', 'f1'],
            ['bertscore_precision', 'bertscore_recall', 'bertscore_f1']
        ),
        'bluert': (
            evaluate.load('bleurt', config_name='BLEURT-20'),
            {},
            ['scores'],
            ['bleurt']
        ),
    }

    ######## CALCULATE PER INSTANCE SCORES ########
    all_scores = {}
    for name, (scorer, kwargs, keys, save_keys) in scorers.items():
        scores = scorer.compute(references=references, predictions=predictions, **kwargs)
        for score_key, save_key in zip(keys, save_keys):
            all_scores[save_key] = scores[score_key]

    cohorts = [
        ('all', list(range(num_test))),
    ]

    subsets = full_df['dataset'].unique().tolist()
    for subset in subsets:
        # Don't include anything after num_test (section-level)
        indices = full_df[full_df['dataset'] == subset].index.tolist()
        cohorts.append((f'dataset-{subset}', indices))

    if args.task == 'taskB':
        for ind, division in enumerate(SECTION_DIVISIONS):
            start = (ind + 1) * num_test
            end = (ind + 2) * num_test
            cohorts.append((f'division-{division}', list(range(start, end))))

        # ######## CALCULATE PER-LENGTH SCORES (bigger than --note_length_cutoff=512 vs not) ########
        df_shortsrc = full_df[full_df['src_len'] <= args.note_length_cutoff]
        if len(df_shortsrc) > 0:
            indices = df_shortsrc.index.tolist()
            cohorts.append(('shorter-src', indices))

        df_longsrc = full_df[full_df['src_len'] > args.note_length_cutoff]
        if len(df_longsrc) > 0:
            indices = df_longsrc.index.tolist()
            cohorts.append(('longer-src', indices))

    outputs = {k: filter_and_aggregate(all_scores, idxs) for (k, idxs) in cohorts}

    # ###### OUTPUT TO JSON FILE ########
    fn_out = f'{args.experiment}_results.json'
    print(f'Saving results to {fn_out}')
    with open(fn_out, 'w') as fd:
        json.dump(outputs, fd, indent=4)

    for cohort, obj in outputs.items():
        print(cohort)
        for k, v in obj.items():
            print(f'\t{k} -> {round(v, 3)}')
        print('\n')
