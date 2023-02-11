"""
This is a courtesy script divides src/tgt text into seperate text files.
Order of the original dataframe is preserved.

Text files are also outputted for ease of browsing.

Everything will be outputted in the same directory as the original file.
"""
import sys
import os
import re

import pandas as pd

#metadata_columns = [  'dataset', 'encounter_id' ]
TRANSCRIPT_COLUMN = 'dialogue'
NOTE_COLUMN = 'note'


def divide_and_output( df, outdir, prefix, id_column='encounter_id' ) :

    columns = df.columns
    metadata_columns = [ x for x in columns if x not in [ TRANSCRIPT_COLUMN, NOTE_COLUMN ] ]

    #first split out metadata file (will need this for evaluating by different sets)
    df[ metadata_columns ].to_csv( '%s/%s_metadata.csv' %( outdir, prefix ), index=False )

    #output src and targets
    if TRANSCRIPT_COLUMN in columns :
        df[ TRANSCRIPT_COLUMN ].apply( lambda x: re.sub( '[ ]+', ' ', x.replace( '\n', ' ' ) ) ).to_csv( '%s/%s.src' %( outdir, prefix ), header=False, index=False )
    if NOTE_COLUMN in columns :
        df[ NOTE_COLUMN ].apply( lambda x: re.sub( '[ ]+', ' ', x.replace( '\n', ' __lf1__ ' ) ) ).to_csv( '%s/%s.tgt' %( outdir, prefix ), header=False, index=False )

    #create folder to output text files
    os.makedirs( '%s/output/%s' %( outdir, prefix ), exist_ok=True )

    for _, row in df.iterrows() :

        encounter_id = row[ id_column ]

        if TRANSCRIPT_COLUMN in columns :
            dialogue = row[ 'dialogue' ]
            fn = '%s/output/%s/%s.transcript.txt' %( outdir, prefix, encounter_id )
            write_file( dialogue, fn )

        if NOTE_COLUMN in columns :
            note = row[ 'note' ]
            fn = '%s/output/%s/%s.report.txt' %( outdir, prefix, encounter_id )
            write_file( note, fn )


def write_file( text, fn ) :
    with open( fn, 'w' ) as f :
        f.write( text )


if __name__ == "__main__" :
    """
    Assumes input is *.csv according to prepared files (which may have extra metadata in addition to either
    dialogue note, or both ).
    Will output to same directory as file.
    """
    if len( sys.argv ) > 1 :
        fn = sys.argv[1]
        id_column = [ sys.argv[2] if len(sys.argv)>2 else 'encounter_id' ][0]
    else :
        print( 'usage: python divide_and_output_files.py <*.csv>')
        sys.exit( 0 )
    
    file_dir = os.path.dirname( fn )
    prefix = fn.split( '/' )[-1].replace( '.csv', '' )

    print( 'input csv: %s' %fn )
    print( 'outputting to: %s' %file_dir )

    df = pd.read_csv( fn )
    divide_and_output( df, file_dir, prefix, id_column=id_column )