$usage = "Usage: perl eval.pl qrel inputDir outputDir \n";

$arg = 0;
$qrel = $ARGV[$arg++] or die $usage;
$inputDir = $ARGV[$arg++] or die $usage;
$outputDir = $ARGV[$arg++] or die $usage;


opendir(DIR, $inputDir) or die "can't open a directory";
$ct=0;
while (my $file = readdir(DIR)) {
    next if ($file =~ m/^\./);

    my $dest = $outputDir."/".$file.".eval";
    my $run = $inputDir."/".$file;

    `perl metrics/cubeTest_dd.pl $qrel $run 1000 > $dest`;

    $ct++;
}

