$usage = "Usage: perl eval.pl inputDir  \n";

$arg = 0;
$inputDir = $ARGV[$arg++] or die $usage;


opendir(DIR, $inputDir) or die "can't open a directory";
$ct=0;
while (my $file = readdir(DIR)) {
    next if ($file =~ m/^\./);

    my $run = $inputDir."/".$file;


    open (RUN, $run) || die "$0: cannot open \"$run\": !$\n";
    while (<RUN>) {
      s/[\r\n]//g;

      my @data = split(/,/,$_);

      if ($data[1] eq "all"|| $data[1] eq "amean" || $data[1] eq "mean") {
	  print $_, "\n";
      }
   }
   close (RUN);

   $ct++;
}

