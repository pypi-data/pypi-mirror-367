<h1 align='center'> DNA IBP Command Line Interface </h1>
CLI application for the DNA analyser IBP API wrapper (https://github.com/patrikkaura/dna-analyser-ibp)

## Installation requirements

* Python v.3.10 or better
* pip

## Installation guide

Run the following command in your command line

```command line
pip install dna-ibp
```

<h2>Getting started</h2>

Upon entering any command prefaced by `dna-ibp`, the user is prompted to enter their DNA analyser (https://bioinformatics.ibp.cz/) credentials.

```command line
C:\Users\kryst>dna-ibp sequence show all
Enter your email        example@example.com
Enter your password
2025-07-31 13:03:51.383532 [INFO]: User example@example.com is trying to login ...
2025-07-31 13:03:51.612553 [INFO]: User example@example.com is successfully loged in ...
```
This login session lasts for 60 minutes or can be disconnected prematurely by using the `--reset`/`-r` command:

```command line
C:\Users\kryst>dna-ibp --reset
2025-07-31 13:07:26.229684 [INFO]: User example@example.com logged out...
```

The `--help`/`-h` command can be used after any previous command to list possible sub-commands or arguments:

```command line
C:\Users\kryst>dna-ibp --help
usage: dna-ibp [-h] [--version] [--reset] {sequence,g4hunter,rloop,zdna,cpx,g4killer,p53} ...

positional arguments:
  {sequence,g4hunter,rloop,zdna,cpx,g4killer,p53}
    sequence            Parser for sequence related operations.
    g4hunter            Parser for methods of the G4Hunter tool.
    rloop               Parser for methods of the R-loop tracker tool.
    zdna                Parser for methods of the Z-DNA hunter tool.
    cpx                 Parser for methods of the CpX hunter tool.
    g4killer            Parser for methods of the G4Killer tool.
    p53                 Parser for methods of the P53 predictor tool.

options:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --reset, -r
```

## Usage examples

* User wants to upload a sequence with NCBI ID `NC_010000`, name `Shewanella baltica` and tags `SMALL` and `PLASM`:

`C:\Users\kryst>dna-ibp sequence create --id NC_010000 --name "Shewanella baltica" --tags SMALL PLASM`

***

* User wants to analyse all uploaded sequences using the R-loop tracker tool, with default parameters:

`C:\Users\kryst>dna-ibp rloop analyse all`

***

* User wants to display the latest G4Hunter analysis result:

`C:\Users\kryst>dna-ibp g4hunter show -1`

***

* User wants to export all Z-DNA hunter analysis results on their account to a .csv file to the current working directory:

`C:\Users\kryst>dna-ibp zdna export all --path ./`

***

* User wants to delete a CpX analysis result with the ID: `7c6e6d56-da6e-4355-bcc8-5601465d646e`:

`C:\Users\kryst>dna-ibp cpx delete 7c6e6d56-da6e-4355-bcc8-5601465d646e`

***

* User wants to analyse a sequence `GGACATGCCCGGGCATGGGG` using G4Killer tool (with complementary sequence setting turned OFF):

`C:\Users\kryst>dna-ibp g4killer run GGACATGCCCGGGCATGTCC --no-comp`

## Documentation

To see all valid commands see the [full list of CLI commands](commands.md).

## Dependencies
DNA_analyser_IBP >=3.7.1

## Authors
* **Kryštof Kotrys** - *Main Developer* - [krystofkotrys](https://github.com/krystofkotrys)

## License

This project is licensed under the GPL-3.0 License - see the [LICENSE.md](LICENSE.md) file for details.
