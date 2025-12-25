#!/usr/bin/env perl
use strict;
use warnings;
use open qw(:std :utf8);

my $input  = 'combined.dot';
my $output = 'output.dot';
die "File not found: $input\n" unless -f $input;

open my $IN,  '<', $input  or die "Can't open $input: $!";
open my $OUT, '>', $output or die "Can't write to $output: $!";

print ">>> Processing $input …\n";

my @chunk;            # lines of the current chunk
my %map;              # NodeN -> label for the current chunk
my $chunk_name = '';  # the // From … line that starts the chunk
my $line_no = 0;

sub flush_chunk {
    return unless @chunk;       # nothing to flush
    print ">>  Rewriting chunk: $chunk_name\n";
    print ">>   mappings: ", join(', ', map { "$_➜\"$map{$_}\"" } keys %map), "\n";

    # Phase B – rewrite
    for my $raw (@chunk) {
        my $line = $raw;  # copy
        for my $node ( sort { length $b <=> length $a } keys %map ) {
            my $quoted = qq{"$map{$node}"};    # "Label"
            $line =~ s/\b\Q$node\E\b/$quoted/g;
        }
        print $OUT $line;
    }

    # reset for next chunk
    @chunk = ();
    %map   = ();
}

while ( my $line = <$IN> ) {
    ++$line_no;

    # Start of a new chunk?
    if ( $line =~ m{^\s*//\s*From\s} ) {
        flush_chunk();                 # finish previous chunk
        $chunk_name = $line =~ s/^\s*//r;   # store comment without leading spaces
    }

    # Phase A – collect mapping
    if ( $line =~ /^\s*(Node\d+)\s+\[label="([^"]+)"/ ) {
        my ($node, $label) = ($1, $2);
        $map{$node} = $label;
    }

    push @chunk, $line;                # keep line for later rewrite
}

flush_chunk();     # flush final chunk
close $IN;
close $OUT;

print "Done. Output written to $output\n";

