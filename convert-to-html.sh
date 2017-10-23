#!/bin/bash

# converts the using-aws-batch-at-fred-hutch.md document to HTML,
# adding a TOC in the process:

pandoc --include-before-body=header.md --toc -V toc-title:"Table of Contents" --template=template.markdown -o output-with-toc.md using-aws-batch-at-fred-hutch.md

pandoc output-with-toc.md -o using-aws-batch-at-fred-hutch.html

rm output-with-toc.md
