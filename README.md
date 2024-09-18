# transducer-bib

This repository contains a collection of bibtex entries for papers and books
that started as a collection of papers on transducers and automata theory. 
It has since grown to include papers on well-quasi-orderings, model theory, and
other topics that I find relevant to the study of transducers.

The bibliography is explorable online at the [github pages][ghpages] of this
repository.

[ghpages]: https://aliaumel.github.io/transducer-bib


## Files

- [automata.bib](transducer.bib): basic automata papers and books.
- [model-theory.bib](model-theory.bib): the bare minimum of model theory that
  applies to finite words.
- [wqos.bib](wqos.bib): well-quasi-orderings and their applications to automata
  theory.
- [sublinear.bib](sublinear.bib): transductions of at most linear growth (mealy
  machines, sequential transducers, rational transducers, regular transducers
  etc.).
- [polyregular.bib](polyregular.bib): transductions of polynomial growth.
- [rational-series.bib](rational-series.bib): rational series and their
  applications to automata theory. This may overlap with the
  [polyregular.bib](polyregular.bib) file when the output of the polyregular
  function is unary. In general, if the paper is mostly about rational series
  (even of polynomial growth), it should go here.

## Contributing

Please feel free to open a pull request to add papers or books to the
appropriate file. The entries are formatted quite uniformly, so please try
to follow the same style, and in particular

- try to find the DOI of the paper and include it in the `doi` field.
- if possible also add `isbn` and `url` in case the DOI is not available.
- do not put abstracts.
- do not put keywords.
- if you happen to have the pdf file please add its `sha256` hash to the
  `sha256` field. 
- optionally, you can also add the `md5` hash.

In case several papers correspond to a given bibtex entry (e.g., an arxiv
preprint, a conference version, a revised conference version) please add the
`eprint` field with the arxiv id *of the latest revision*, and the list of
hashes of the corresponding pdf files.

## How to use

Well, you can just clone the repository or use it as a [git submodule] of your
paper.

[git submodule]: https://git-scm.com/book/en/v2/Git-Tools-Submodules
