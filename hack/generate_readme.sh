#!/usr/bin/env bash
parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
cp $parent_path/README-base.md $parent_path/../README.md
typer tappr.main utils docs >> $parent_path/../README.md