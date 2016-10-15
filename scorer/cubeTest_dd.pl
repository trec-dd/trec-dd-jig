#!/usr/bin/perl

## CubeTest Implementation For TREC Dynamic Domain Track Evaluation

## For Linux Unix Platform

## This software is released under an MIT/X11 open source license. Copyright 2015 @ Georgetown University

## Version: lgc

## Date: 12/03/2014

#########################################


#### Parameter setup and initialization
$usage = "Usage: perl score/cubeTest.pl qrel run_file cutoff\n
- qrel: qrel file. It is a trec qrel file that converted from topics.xml. Its format is topic_id subtopic_id doc_no rating, which is located at ./truth_data/qrel.txt.\n
- run_file: Your run for submission.  It is in TREC format.\n
- cutoff: the number of iterations where you run cubetest over your results.\n
";
#index_path: index path \n

$MAX_JUDGMENT = 4; # Maximum gain value allowed in qrels file.

$MAX_HEIGHT = 5; #max hight for the test cube

$beta =1; #a factor decide recall-oriented or precision-oriented

$gamma = 0.5;

$arg = 0;
$QRELS = $ARGV[$arg++] or die $usage;
$RUN = $ARGV[$arg++] or die $usage;
$K = $ARGV[$arg++] or die $usage; 
#$index = $ARGV[$arg++] or die $usage; 

# $topic $docno $subtopic $judgement
%qrels=();
#$topic $subtopic $area
%subtopicWeight=();
# $topic $subtopic $gainHeights
%currentGainHeight=();
# $topic $subtopic $occurrences
%subtopicCover = ();
# $docID $docLength
%docLengthMap = ();
%seen=();

#########################################

#### Read qrels file(groundtruth), check format, and sort
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
}
close (QRELS);

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

        $subTWeigt = 1;
        $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic}=$final_qrel;

	if(!exists $subtopicWeight{$tmpTopicKey}{$tmpSubtopic}){
           if(defined $subTWeigt && length $subTWeigt> 0){
              $subtopicWeight{$tmpTopicKey}{$tmpSubtopic} = $subTWeigt;
           }
           $currentGainHeight{$tmpTopicKey}{$tmpSubtopic} = 0;
           $subtopicCover{$tmpTopicKey}{$tmpSubtopic} = 0;
        }

        $seen{$tmpTopicKey}++;
     }
  }
}

##### Normalize relevance rating
=cut
foreach my $tmpTopicKey (keys %qrels){
  my %documents = %{$qrels{$tmpTopicKey}};
  my $maxRel = 0;
  foreach my $tmpDoc (keys %documents){
     my %subtopics = %{$documents{$tmpDoc}};
     foreach my $tmpSubtopic (keys %subtopics){
        if($qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic} > $maxRel){
	   $maxRel = $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic};
        }
     }
  }

  foreach my $tmpDoc (keys %documents){
     my %subtopics = %{$documents{$tmpDoc}};
     foreach my $tmpSubtopic (keys %subtopics){
        $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic} = $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic}/$maxRel;
        #print "$tmpTopicKey $tmpDoc $tmpSubtopic ", $qrels{$tmpTopicKey}{$tmpDoc}{$tmpSubtopic} , "\n";
     }
  }
}
=cut

#########################################

#### Normalize subtopic weight

for my $tkey (keys %subtopicWeight){
    my %subs = %{$subtopicWeight{$tkey}};
    my $maxWeight = &getMaxWeight($tkey);
    for my $skey (keys %subs){        
        $subtopicWeight{$tkey}{$skey} = $subtopicWeight{$tkey}{$skey}/$maxWeight;
    }
}

sub getMaxWeight{
  my ($topic) = @_;
  my $maxWeight = 0;
  my %subtopics = %{$subtopicWeight{$topic}};
  for my $skey (keys %subtopics){
      $maxWeight += $subtopics{$skey};
  }
  return $maxWeight;
}

$topics = 0;
$runid = "?????";

#########################################

#### Read run file(returned document rank lists), check format, and sort
$maxIteration=0;
open (RUN, $RUN) || die "$0: cannot open \"$RUN\": !$\n";
my $rank = "";
while (<RUN>) {
  s/[\r\n]//g;
  ($topic, $iteration, $docno, $score, $rel, $subtopics) = split ('\s+');
  #($topic, $Q0, $docno, $rank, $score, $runid, $iteration) = split ('\s+');
  #if($RUN !~ /GU_RUN/){
     $iteration += 1;
  #}
  if($maxIteration < $iteration){
	$maxIteration = $iteration;
  }
  $doclength = 1; #`./bin/getDocLength $docno $index`;
  #$doclength =~ s/[\r\n]//g;
  $topic =~ s/[\r\n]//;
  die "$0: format error on line $. of \"$RUN\"\n"
    unless
      $docno;
  $run[$#run + 1] = "$topic $docno $score $iteration";

  if(defined $doclength && length $doclength > 0){
     if(!exists $docLengthMap{$docno}){
     	$docLengthMap{$docno} = $doclength;
     }
  } 
}
#########################################

#### Process runs: compute measures for each topic and average

print "run_id,topic,ct\@$K,avg_ct\@$K\n";
$topicCurrent = "-1";
for ($i = 0; $i <= $#run; $i++) {
  ($topic, $docno, $score, $iteration) = split (' ', $run[$i]);
  if ($topic ne $topicCurrent) {
    if ($topicCurrent ne "-1") {
      &topicDone ($RUN, $topicCurrent, \@docls, \@iterations );
      $#docls = -1;
      $#iterations = -1;
    }
    $topicCurrent = $topic;
  }
  $docls[$#docls + 1] = $docno;
  $iterations[$#iterations + 1] = $iteration;
}
if ($topicCurrent ne "-1") {  
  &topicDone ($RUN, $topicCurrent, \@docls, \@iterations);
  $#docls = -1;
  $#iterations = -1;
}
if ($topics > 0) {
  $ctAvg = $ctTotal/$topics;
  $accelAvg = $ct_accuTotal/$topics;

  printf "$RUN,all,%.10f,%.10f\n",$ctAvg,$accelAvg;
} else {
  print "$RUN,all,0.00000,0.00000\n";
}

exit 0;

#########################################

#### Compute and report information for current topic

sub topicDone {
  my ($runid, $topic, $ref_docls, $ref_iterations) = @_;
  if (exists $seen{$topic}) {
    my $_ct = &ct($K, $topic, $ref_docls, $ref_iterations);
    my $_time = &getTime($K, $topic, $ref_docls, $ref_iterations);

    my $ct_accu = 0;
    my $limit = ($K <= $maxIteration? $K : $maxIteration);
    my @tmp_docs = @{$ref_docls};
    my @tmp_iterations = @{$ref_iterations};
    my $lastIndex = $#tmp_docs + 1;

    my $docCount = 0;
    for($count =0 ; $count < $lastIndex; $count++){
        my $curIteration = $tmp_iterations[$count];
        if($curIteration > $K){
	   last;
        }

        &clearEnv;

        my $accel_ct = &ct_by_doc($count + 1, $topic, $ref_docls, $ref_iterations);
        my $accel_time = &getTime($curIteration, $topic, $ref_docls, $ref_iterations);

	$docCount++;
        $ct_accu += $accel_ct / $accel_time;
    }
    if($docCount != 0){
       $ct_accu = $ct_accu / $docCount;
    }else{
       $ct_accu = 0;

       #print "error: cut $K $lastIndex " ,$runid, " ", $topic, "\n";

       #for my $index (0 .. $#tmp_docs){
       #    print $tmp_docs[$index], " ", $tmp_iterations[$index] , "\n";
       #}

       #print "====================\n";

       #exit -1;
    }
    $ct_accuTotal += $ct_accu;
    
    my $ct_speed = $_ct / $_time;
    $ctTotal += $ct_speed;
    $topics++;
    printf  "$runid,$topicCurrent,%.10f,%.10f\n",$ct_speed,$ct_accu;
    &clearEnv;
  }
}

sub clearEnv{
  for my $tkey (keys %currentGainHeight){
      my %subs = %{$currentGainHeight{$tkey}};
      for my $skey (keys %subs){
          $currentGainHeight{$tkey}{$skey}=0;
      }
  }

  for my $tkey (keys %subtopicCover){
      my %subs = %{$subtopicCover{$tkey}};
      for my $skey (keys %subs){
          $subtopicCover{$tkey}{$skey}=0;
      }
  }  
}

sub ct_by_doc {
 my ($k, $topic, $ref_docls, $ref_iterations) = @_;

 my @local_docls = @{$ref_docls};
 my @local_iterations = @{$ref_iterations};

 my ($i, $score) = (0, 0);
 for ($i = 0; $i <= $#local_docls && $i < $k ; $i++) {
   my $docGain = &getDocGain($topic, $local_docls[$i], $i + 1);
   $score += $docGain;
 }

 return $score/$MAX_HEIGHT; #normalization by max value
}

#########################################

#### Compute ct over a sorted array of gain values, reporting at depth $k

sub ct {
 my ($k, $topic, $ref_docls, $ref_iterations) = @_;

 my @local_docls = @{$ref_docls};
 my @local_iterations = @{$ref_iterations};

 my ($i, $score) = (0, 0);
 for ($i = 0; $i <= $#local_docls && $k >= $local_iterations[$i] ; $i++) {
   my $docGain = &getDocGain($topic, $local_docls[$i], $i + 1);
   $score += $docGain;
 }

 return $score/$MAX_HEIGHT; #normalization by max value
}

sub getDocGain{
  my ($topic, $docno, $rank) = @_;
  my $rel = 0;
  
  if(exists $qrels{$topic}{$docno}){
    my %subtopics = %{$qrels{$topic}{$docno}};
    my $inFlag = -1;
    for my $subKey(keys %subtopics){
        if(&isStop($topic, $subKey) < 0 ){
           my $boost = 1;
           for my $subKey1(keys %subtopics){
               if(exists $currentGainHeight{$topic}{$subKey1} && $subKey ne $subKey1){
                  my $areaW = &getArea($topic, $subKey1);
                  my $heightW =  $currentGainHeight{$topic}{$subKey1};
                  $boost += $beta * $areaW * $heightW;
               }               
           }

           my $pos = 0;
           if(exists $subtopicCover{$topic}{$subKey}){
              $pos = $subtopicCover{$topic}{$subKey};
           }

           my $height = &getHeight($topic, $docno, $subKey,$pos + 1, $boost);

           my $area = &getArea($topic, $subKey);

           $rel += $beta * $area * $height;
        }
    }

    for my $subKey (keys %subtopics){
           $subtopicCover{$topic}{$subKey}++;
    }
    
  }
  
  return $rel;   
}

#########################################

#### Get subtopic importance

sub getArea{
  my ($topic, $subtopic) = @_;
  
  if(exists $subtopicWeight{$topic}{$subtopic}){
     return $subtopicWeight{$topic}{$subtopic};
  }else{
     $subtopicWeight{$topic}{$subtopic} = &getDiscount($subtopic)/&getMaxArea($topic);
     return $subtopicWeight{$topic}{$subtopic};
  }

  return 0;
}

sub getHeight{
  my ($topic, $docno, $subtopic, $pos, $benefit) = @_;
  
  #set $benefit = 1 if don't want to consider boost effect
  $benefit = 1;
  my $rel = &getHeightDiscount($pos) * $qrels{$topic}{$docno}{$subtopic} * $benefit;

  my $currentHeight = $currentGainHeight{$topic}{$subtopic};

  if($currentHeight + $rel > $MAX_HEIGHT){
     $rel = $MAX_HEIGHT - $currentHeight;
  }

  $currentGainHeight{$topic}{$subtopic} += $rel;

  return $rel;
}

sub getHeightDiscount{
  my ($pos) = @_;

  return ($gamma) ** $pos;
}

sub isStop{
  my ($topic, $subtopic) = @_;
  if($currentGainHeight{$topic}{$subtopic} < $MAX_HEIGHT){
    return -1;
  }

  return 0;
}

#sub getTime{
#  my ($pos, $topic, $ref_docls, $ref_iterations) = @_;
#  my @local_docls = @{$ref_docls};
#  my @local_iterations = @{$ref_iterations};
#
#  my $time =0;
#  for (my $count = 0; $local_iterations[$count] <= $pos && $count <= $#local_docls ; $count++) {
#       my $prob = 0.39;
#       if (exists $qrels{$topic}{$local_docls[$count]}){
#         $prob = 0.64;
#       }
#
# 	$time += 4.4 + (0.018*$docLengthMap{$local_docls[$count]} +7.8)*$prob;
#  }
#
#  return $time;
#}

sub getTime{
  my ($pos, $topic, $ref_docls, $ref_iterations) = @_;

  my @local_iterations = @{$ref_iterations};
  my $max_iteration = $local_iterations[-1];

  my $time = $pos;

  if($pos > $max_iteration){
     $time = $max_iteration;
  }

  return $time;
}

sub getDiscount{
  my ($pos) = @_;

  return 1/(log($pos + 1)/log(2));
}

sub getMaxArea{
  my ($topic) = @_;

  my %subtopics = %{$subtopicCover{$topic}};
  my @subs = keys %subtopics;
  my $subtopicNum = $#subs + 1;

  my $maxArea = 0;
  for($count = 0;$count < $subtopicNum; $count++){
     $maxArea += &getDiscount($count + 1);
  }

  return $maxArea;
}
