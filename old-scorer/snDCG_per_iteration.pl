#!/usr/bin/perl -w

# Graded relevance assessment script for the TREC 2010 Web track
# Evalution measures are written to standard output in CSV format.
# 
# Currently reports only nSDCG
# (see http://learningtorankchallenge.yahoo.com/instructions.php)

# perl .pl  truth_file run_file 5

$usage = "usage: $0 qrels run_file iteration-capacity [discounter(BQ)]";
$version = "version 1.2 (Tue Oct 12 15:58:46 EDT 2010)";

#$MAX_JUDGMENT = 4; # Maximum gain value allowed in qrels file.
$K = 10000;        # Reporting depth for results. suficiantly large
$BQ = 2;           # 2 is no patiant scan, 10 is patient scan

if ($#ARGV >= 0 && ($ARGV[0] eq "-v" || $ARGV[0] eq "-version")) {
  print "$0: $version\n";
  exit 0;
}

if ($#ARGV >= 0 && $ARGV[0] eq "-help") {
  print "$usage\n";
  exit 0;
}

die $usage unless $#ARGV >= 2;
$QRELS = $ARGV[0];
$inputRun = $ARGV[1];
$CAPACITY = $ARGV[2];
if($#ARGV >= 3){
   $BQ = $ARGV[3];
}


my %qrels=();
my %seen=();
my %subtopicCT = ();
# Read qrels file, check format, and sort
open (QRELS, $QRELS) || die "$0: cannot open \"$QRELS\": !$\n";
my %tmpQrel = ();
while (<QRELS>) {
  s/[\r\n]//g;
  ($topic, $subtopic, $docno, $passage, $judgment) = split ('\s+');

  $topic =~ s/[\r\n]//;

  die "$0: format error on line $. of \"$QRELS\"\n"
    unless
      $judgment =~ /^-?[0-9.]+$/; #&& $judgment <= $MAX_JUDGMENT
  if ($judgment > 0) {
      $tmpQrel{$topic}{$docno}{$subtopic}{$passage} = $judgment;
  }
  if ($judgment == 0) {
      $tmpQrel{$topic}{$docno}{$subtopic}{$passage} = 1;
  }
  $subtopicCT{$topic}{$subtopic}++;
}
close (QRELS);

my %idealDCG = ();
my %qrelDoc = ();
foreach my $tmpTopicKey (keys %tmpQrel){
  my %documents = %{$tmpQrel{$tmpTopicKey}};
  foreach my $tmpDoc (keys %documents){
     my %subtopics = %{$documents{$tmpDoc}};
     foreach my $tmpSubtopic (keys %subtopics){
        my %passages = %{$subtopics{$tmpSubtopic}};
        my @rels = ();
        foreach my $tmpPassage (keys %passages){
           push(@rels, $passages{$tmpPassage});
        }
        my @tmpRel = sort {$b <=> $a} @rels;
        my $final_qrel = 0;
        my $rank = 0;
        foreach my $element(@tmpRel){
           $rank++;
           my $discount = log($rank+1)/log(2);
           $final_qrel += $element / $discount;
        }

        #$subTWeigt = 1;
        $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic}=$final_qrel;
	if(!exists $qrelDoc{$tmpTopicKey}{$tmpDoc}){
	   $qrelDoc{$tmpTopicKey}{$tmpDoc} = $final_qrel;
        }else{
	   $qrelDoc{$tmpTopicKey}{$tmpDoc} += $final_qrel;
        }

        $seen{$tmpTopicKey}++;
     }
  }
}

foreach my $tmpTopicKey (keys %qrelDoc){
  my %documents = %{$qrelDoc{$tmpTopicKey}};
  my @subtopics = keys %{$subtopicCT{$tmpTopicKey}};
  my @relevance  = ();
  my $index = 0;
  foreach my $tmpDoc (keys %documents){
     $qrelDoc{$tmpTopicKey}{$tmpDoc} /= ($#subtopics + 1);
     $relevance[$index] = $qrelDoc{$tmpTopicKey}{$tmpDoc};
     $index++;
  }
  my @sortedRel = sort {$b <=> $a} @relevance;
  #if($tmpTopicKey eq "DD15-1") {print "sorted rel : @sortedRel \n";}
  my $rank = 0;
  my $score = 0;
  my $itCT = 1;
  $index = 0;
  foreach my $rel (@sortedRel){
     $index++; #count element number
     $rank++;

     my $discount = log($rank+1)/log(2);
     $score +=  (2**$rel - 1) / $discount / (1 + log($itCT)/log($BQ));
     $idealDCG{$tmpTopicKey}[$index - 1] = $score;

     if($index%$CAPACITY == 0){
        $rank = 0;
        $itCT ++;
     }
  }

  #if($tmpTopicKey eq "DD15-1") {
  #   my @msg = @{$idealDCG{$tmpTopicKey}};
  #print("test $#msg : @msg  \n");}

}

#for my $qkey (keys %qrels){
#    print $qkey, ":";
#    my %q = %{$qrels{$qkey}};
#    for my $tkey (keys %q){
#       print $tkey, ":";
#       my %t = %{$q{$tkey}};
#       for my $skey (keys %t){
#          print $skey , ":";
#          my $s = $t{$skey};
#          print $s , "\n";
#       }
#    }
#}


    #my $dest = $inputRun.".eval";
    my $RUN = $inputRun;
    $topics = 0;
    $runid = $RUN;
    @run = ();

# Read run rile, check format, and sort
open (RUN, $RUN) || die "$0: cannot open \"$RUN\": !$\n";
my $rank = "";
while (<RUN>) {
    s/[\r\n]//g;
    my ($topic, $iteration, $docno, $score, $rel, $subtopics) = split ('\s+');

    $iteration += 1;

    #$doclength = 1; #`./bin/getDocLength $docno $index`;
    #$doclength =~ s/[\r\n]//g;
    $topic =~ s/[\r\n]//;

    $run[$#run + 1] = "$topic $docno $score $iteration";
}
close(RUN);

#@run = sort runOrder (@run);

#for my $r (@run){
#  print $r, "\n";
#}

# Process runs: compute measures for each topic and average
#open($fh, ">$dest");
#print $fh "runid,topic,nsdcg\n";
print "runid,topic,nsdcg\n";
$topicCurrent = "-1";
my $ndcgTotal = 0;
for ($i = 0; $i <= $#run; $i++) {
  my ($topic, $docno, $score, $iteration) = split (' ', $run[$i]);
  if ($topic ne $topicCurrent) {
    if ($topicCurrent ne "-1") {
      #printf $fh  "outsider: topic $topicCurrent gain ct: $#gain   iteration ct: $#iterations \n ";
      my $sdcg = &topicDone ($RUN, $topicCurrent, \@gain, \@iterations);
      $sdcg /= $iterations[-1];
      $ndcgTotal += $sdcg;

      #printf $fh  "$runid,$topicCurrent,%.5f\n",$sdcg;
      printf  "$runid,$topicCurrent,%.5f\n",$sdcg;
      @gain = ();
      @iterations = ();
    }
    $topicCurrent = $topic;
  }
  my $tmpGain = 0;
  if(exists $qrelDoc{$topic}{$docno}){
     $tmpGain = $qrelDoc{$topic}{$docno};
  }
  $gain[$#gain + 1] = $tmpGain;
  $iterations[$#iterations + 1] = $iteration;
}
if ($topicCurrent ne "-1") {
  #printf $fh  "outsider: topic $topicCurrent gain ct: $#gain   iteration ct: $#iterations \n ";
  my $sdcg = &topicDone ($RUN, $topicCurrent, \@gain, \@iterations);
  $sdcg /= $iterations[-1];
  $ndcgTotal += $sdcg;
  #printf $fh  "$runid,$topicCurrent,%.5f\n",$sdcg;
  printf "$runid,$topicCurrent,%.5f\n",$sdcg;
  @gain = ();
  @iterations = ();
}
if ($topics > 0) {
  $ndcgAvg = $ndcgTotal/$topics;
  #printf $fh "$RUN,amean,%.5f\n",$ndcgAvg;
  printf "$RUN,amean,%.5f\n",$ndcgAvg;
} else {
  #print $fh "$RUN,amean,0.00000\n";
  print "$RUN,amean,0.00000\n";
}


#close($fh);
#print($dest);
#system('cat', $dest);

exit 0;

# comparison function for runs: by topic then score then docno
sub runOrder {
  my ($topicA, $docnoA, $scoreA) = split (' ', $a);
  my ($topicB, $docnoB, $scoreB) = split (' ', $b);

  if ($topicA < $topicB) {
    return -1;
  } elsif ($topicA > $topicB) {
    return 1;
  } elsif ($scoreA < $scoreB) {
    return 1;
  } elsif ($scoreA > $scoreB) {
    return -1;
  } elsif ($docnoA lt $docnoB) {
    return 1;
  } elsif ($docnoA gt $docnoB) {
    return -1;
  } else {
    return 0;
  }
}

# compute and report information for current topic
sub topicDone {
  my ($runid, $topic, $gains, $iterations) = @_;
  my($sdcg) = (0);
  if (exists $seen{$topic}) {
    $sdcg = &dcg($K, $topic, $gains, $iterations);
    $topics++;
  }
  return $sdcg;
}

# compute DCG over a sorted array of gain values, reporting at depth $k
sub dcg {
 my ($k, $tid, $tmp_gains, $tmp_iterations) = @_;
 my @gain = @{$tmp_gains};
 my @iterations = @{$tmp_iterations};
 
 #printf $fh  "insider: topic $tid gain ct: $#gain   iteration ct: $#iterations \n ";
 my $pre_iteration = 0;
 if($#iterations >= 0){
    $pre_iteration = $iterations[0];
 }
 my $rank = 1;
 my $itCT = 1;
 my ($i, $dcg_score) = (0, 0);
 my $score = 0;
 for ($i = 0; $i <= ($k <= $#gain ? $k - 1 : $#gain); $i++) {
   if($iterations[$i] != $pre_iteration){
      my @ideal_nDCG = @{$idealDCG{$tid}};
      my $idealGain = 0;
      if($i-1 > $#ideal_nDCG){
         $idealGain = $ideal_nDCG[-1];
      }else{
         $idealGain = $ideal_nDCG[$i-1];
      }
 
      $score += $dcg_score /(1+log($itCT)/log($BQ));

      #print " it_sdcg:$dcg_score ";
      
      $pre_iteration = $iterations[$i];
      $dcg_score = 0;
      $rank = 1;
      $itCT ++;
   }
   my $rel = $gain[$i];
   $dcg_score += (2**$rel - 1)/(log ($rank + 1)/log(2));

   #if($tid eq "DD15-1") {
   #   my $mk = (2**$rel - 1)/(log ($rank + 1)/log(2));
   #   print " $mk";
   #}

   $rank ++;
   #)/(1+log($data[0])/log($BQ));
 }

 #if($tid eq "DD15-1") {
 #     print "\n";
 #  }

 if($#gain >= 0){
   my @ideal_nDCG = @{$idealDCG{$tid}};
   my $idealGain = 0;
   if($i-1 > $#ideal_nDCG){
      $idealGain = $ideal_nDCG[-1];
   }else{
      $idealGain = $ideal_nDCG[$i-1];
   }

   $score += $dcg_score /(1+log($itCT)/log($BQ));
   $score /= $idealGain;
      
   #print " it_sdcg:$dcg_score \n";
      
 }
 return $score;
}

