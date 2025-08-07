# help.py

class SequenceHelp:
    """
    Help reponses for api.sequence methods
    """

    SEQUENCE: str = "Parser for sequence related operations."
    SEQ: str = "Sequence to be processed by related methods."

    LOAD: str = "Load sequence(s) uploaded in your DNA analyser account."
    DELETE: str = "Delete chosen sequence(s) from your DNA analyser account."
    NUCL_COUNT: str = "Recount nucleotides for a given sequence."

    UPLOAD: str = "Parser for uploading sequences to your DNA analyser."
    FILE: str = "Upload a sequence by providing path to a file (.txt of FASTA)"
    ID: str = "Upload a sequence via NCBI ID."
    TEXT: str = "Upload a sequence via pasting a string."

    CIRCULAR: str = "Specify whether the sequence is circular or not (--circular or --no-circular)."
    TAGS: str = "(OPTIONAL) Specify tags associated with the uploaded sequence."
    NUCL_TYPE: str = "Specify whether the sequence nucleic type (choices: %(choices)s, default val: %(default)s)."
    NAME: str = "Specify name of the uploaded sequence."

class G4HunterHelp:
    """
    Help responses for api.g4hunter methods
    """

    G4HUNTER: str = "Parser for methods of the G4Hunter tool."
 
    DELETE: str = "Delete chosen analyse result(s) from your DNA analyser account."

    ANALYSE: str = "Analyse the provided sequence by G4Hunter algorithm"
    SEQUENCE: str = "Choose sequence(s) which should be analysed by the G4 Hunter algorithm"
    TAGS: str = "(OPTIONAL) Add tags to analyse result(s)."
    THRESHOLD: str = "Minimal G4Hunter score to be classified as a hit."
    WINDOW_SIZE: str = "Minimal required number of consecutive nucleotide bases to be classified as a hit."

    SHOW: str = "Display selected analyse result(s) in the command line"
    DETAILS: str = "Show details of the selected analyse result."

    EXPORT: str = "Export the provided G4Hunter result(s) as a CSV file."
    RESULT: str = "Specify the analyse result(s) to be selected."
    PATH: str = "Path where the CSV file should be saved."
    AGGREGATE: str = "Specify whether the CSV file should be grouped or not. Usage: --aggregate or --no-aggregate (default %(default)s)."

class G4KillerHelp:
    """
    Help reponses for api.g4killer methods
    """

    G4KILLER: str = "Parser for methods of the G4Killer tool."
    RUN: str = "Run the G4Killer algorithm on the provided sequence."
    SEQUENCE: str = "Specify the sequence(s) to be modified by G4Killer algorithm."
    COMPLEMENTARY: str = "Specify whether the analysed sequence is G-rich (false) or C-rich (true). Usage: --complementary or --no-complementary (default %(default)s)."
    THRESHOLD: str = "Target G4Hunter score for sequence mutation (default %(default)s)."

class P53Help:
    """
    Help responses for api.p53_predictor methods
    """

    P53: str = "Parser for methods of the P53 predictor tool."
    RUN: str = "Run the P53 predictor algorithm on the provided sequence."
    SEQUENCE: str = "Specify the sequence(s) to be processed by P53 predictor algorithm."

class RLoopHelp:
    """"
    Help responses for api.rloopr methods
    """

    RLOOP: str = "Parser for methods of the R-loop tracker tool."

    DELETE: str = "Delete chosen analyse result(s) from your DNA analyser account."

    ANALYSE: str = "Analyse the provided sequence by R-loop tracker algorithm"
    SEQUENCE: str = "Choose sequence(s) which should be analysed by the R-loop tracker algorithm."
    TAGS: str = "(OPTIONAL) Add tags to analyse result(s)."
    RIZ3G: str = "Select whether the RIZ 3G-cluster should be used to analyse."
    RIZ4G: str = "Select whether the RIZ 4G-cluster should be used to analyse."

    SHOW: str = "Display selected analyse result(s) in the command line"
    DETAILS: str = "Show details of the selected analyse result."

    EXPORT: str = "Export the provided R-loop tracker result(s) as a CSV file."
    RESULT: str = "Specify the analyse result(s) to be selected."
    PATH: str = "Path where the CSV file should be saved."

class ZDnaHelp:
    """
    Help responses for api.zdna methods
    """

    ZDNA: str = "Parser for methods of the Z-DNA hunter tool."

    DELETE: str = "Delete chosen analyse result(s) from your DNA analyser account."

    ANALYSE: str = "Analyse the provided sequence by Z-DNA hunter algorithm"
    SEQUENCE: str = "Choose sequence(s) which should be analysed by the Z-DNA hunter algorithm."
    TAGS: str = "(OPTIONAL) Add tags to analyse result(s)."
    MSS: str = "Minimum sequence size - The minimal length of sequences searched (equal to or larger than 6, default is %(default)s)."
    MODEL: str = "Choose the prediction model (only influences default parameters, default: %(default)s)."
    GC: str = "The score for the GC pair, minimum is 0.1."
    GTAC: str = "The score for the GT or AC pair, minimum is 0."
    AT: str = "The score for the AT pair, minimum is 0."
    MSP: str = "Minimal score percentage - the minimum score of the searched Z-DNA window. The minimum is 12 (%%)."

    SHOW: str = "Display selected analyse result(s) in the command line"
    DETAILS: str = "Show details of the selected analyse result."

    EXPORT: str = "Export the provided Z-DNA hunter result(s) as a CSV file."
    RESULT: str = "Specify the analyse result(s) to be selected."
    PATH: str = "Path where the CSV file should be saved."

class CpXHelp:
    """
    Help responses for api.cpg methods
    """
    CPX: str = "Parser for methods of the CpX hunter tool."

    DELETE: str = "Delete chosen analyse result(s) from your DNA analyser account."

    ANALYSE: str = "Analyse the provided sequence by CpX hunter algorithm"
    SEQUENCE: str = "Choose sequence(s) which should be analysed by the CpX hunter algorithm."
    TAGS: str = "(OPTIONAL) Add tags to analyse result(s)."
    WS: str = "The smallest bp size of the window that can be considered an island (default: %(default)s). Min 10, max 10 000."
    GCP: str = "Minimal CX Percentage: The minimum required nucleotide content of C and X (default: %(default)s). Min 0, max 1."
    O_E_CPG: str = "The minimum required value of observed to expected CpX dinucleotides (default: %(default)s). Min 0, max 1. (Greater is more accurate)"
    ISLAND_MERGE_GAP: str = "The smallest bp gap between two islands which will cause them to merge into one (default: %(default)s). Min 10, max 10 000."
    SECOND_NUCLEOTIDE: str = "The second nucleotide of the island, which can be 'G', 'A', 'T', or 'C' (default: %(default)s)"

    SHOW: str = "Display selected analyse result(s) in the command line"
    DETAILS: str = "Show details of the selected analyse result."

    EXPORT: str = "Export the provided CpX hunter result(s) as a CSV file."
    RESULT: str = "Specify the analyse result(s) to be selected."
    PATH: str = "Path where the CSV file should be saved."    

class Help:
    """
    Unified help responses class
    """

    SEQUENCE: SequenceHelp = SequenceHelp()
    G4HUNTER: G4HunterHelp = G4HunterHelp()
    G4KILLER: G4KillerHelp = G4KillerHelp()
    P53: P53Help = P53Help()
    RLOOP: RLoopHelp = RLoopHelp()
    ZDNA: ZDnaHelp = ZDnaHelp()
    CPX: CpXHelp = CpXHelp()