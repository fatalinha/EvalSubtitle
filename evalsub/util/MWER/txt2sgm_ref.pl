#!/usr/bin/perl
#

select(STDOUT); $|=1;
use warnings;
use Getopt::Std;
getopts('d', \%opts);
my $dbg = $opts{"d"};

my $setName = "MUST-Cinema";
my $src     = "English";
my $tgt     = "French";
my $doc     = "doc_1";

print "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
print "<mteval>\n";
print "<refset setid=\"${setName}\" srclang=\"${src}\" trglang=\"${tgt}\" refid=\"ref\">\n";
print "<doc docid=\"${doc}\">\n\n";
my $id=0;
while(<STDIN>) {
    chop();
    if ($_ ne "") {
        printf "<seg id=\"%03d\">$_</seg>\n", ++$id;
    }
}
print "\n</doc>\n</refset>\n";
print "</mteval>\n";

