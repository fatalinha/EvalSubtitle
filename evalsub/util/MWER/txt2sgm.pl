#!/usr/bin/perl
#

select(STDOUT); $|=1;

use Getopt::Std;
getopts('d', \%opts);
my $dbg = $opts{"d"};

my $setName = "MUST-Cinema";
my $src     = "English";
my $doc     = "doc_1";

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
print "<mteval>\n";
print "<srcset setid=\"${setName}\" srclang=\"${src}\">\n";
print "<doc docid=\"${doc}\">\n\n";
my $id=0;
while(<STDIN>) {
    chop();
    if ($_ ne "") {
        printf "<seg id=\"%03d\">$_</seg>\n", ++$id;
    }
}
print "\n</doc>\n</srcset>\n";
print "</mteval>\n";
