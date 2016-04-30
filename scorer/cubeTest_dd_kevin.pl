#!/usr/bin/perl

## CubeTest Implementation For TREC Dynamic Domain Track Evaluation

## For Linux Unix Platform

## This software is released under an MIT/X11 open source license. Copyright 2015 @ Georgetown University

## Version: lgc

## Date: 12/03/2014

#########################################


# perl cubeTest_v5.pl trec_dd15_qrel.txt ../../data/trec15_dd_runs/
#### Parameter setup and initialization
$usage = "Usage: perl score/cubeTest.pl qrel run_dir\n
- qrel: qrel file. It is a trec qrel file that converted from topics.xml. Its format is topic_id subtopic_id doc_no rating, which is located at ./truth_data/qrel.txt.\n
- run_dir: Your directory of run files for submission.  They are in TREC format.\n
";
#index_path: index path \n

$MAX_JUDGMENT = 4; # Maximum gain value allowed in qrels file.

$MAX_HEIGHT = 5; #max hight for the test cube

$beta =1; #a factor decide recall-oriented or precision-oriented

$gamma = 0.5;

$arg = 0;
$QRELS = $ARGV[$arg++] or die $usage;
$RUN_DIR = $ARGV[$arg++] or die $usage;
# $K = $ARGV[$arg++] or die $usage;
# $tid = $ARGV[$arg++] or die $usage;
#$index = $ARGV[$arg++] or die $usage; 

# $topic $docno $subtopic $judgement
%qrels=();
#$topic $subtopic $area
%subtopicWeight=();
# $topic $subtopic $gainHeights
%currentGainHeight=();
# $topic $subtopic $occurrences
%subtopicCover = ();
# $run $docID $docLength
%docLengthMap = ();
%seen=();

#$run $topic $maxIteration
%maxIterations=();
#$run $topic $docID
%runDocs=();
#$run $topic $iteration
%runIterations=();


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

print "run_id,topic,iteration,ct_gamma=$gamma,avg_ct_gamma=$gamma\n";

# Read files in run dir

opendir (DIR, $RUN_DIR) or die $!;
while (my $RUN = readdir(DIR)) {

  #### Read run file(returned document rank lists), check format, and sort
  # $maxIteration=0;
  if($RUN eq "." or $RUN eq "..") {
    next; # continue if not valid filed
  }
  my $path = "$RUN_DIR$RUN";
  
  open (RUN, $path) || die "$0: cannot open \"$RUN\": !$\n";

  # print "$path\n";

  my $rank = "";
  while (<RUN>) {
    s/[\r\n]//g;
    ($topic, $iteration, $docno, $score, $rel, $subtopics) = split ('\s+');
    #($topic, $Q0, $docno, $rank, $score, $runid, $iteration) = split ('\s+');

    if($RUN !~ /GU_RUN/){
       $iteration += 1;
    }

    $doclength = 1; #`./bin/getDocLength $docno $index`;
    #$doclength =~ s/[\r\n]//g;
    $topic =~ s/[\r\n]//;
    die "$0: format error on line $. of \"$RUN\"\n"
      unless
        $docno;

    # Jiyun, check this, not sure about perl syntax
    if(!exists $maxIterations{$RUN}{$topic}){
      $maxIterations{$RUN}{$topic} = 0;
    }
    
    if($maxIterations{$RUN}{$topic} < $iteration){
      $maxIterations{$RUN}{$topic} = $iteration;
    }

    if(!exists $runDocs{$RUN}{$topic}) {
      $runDocs{$RUN}{$topic} = [];
    }
    if(!exists $runIterations{$RUN}{$topic}) {
      $runIterations{$RUN}{$topic} = [];
    }
    
    # $run[$#run + 1] = "$topic $docno $score $iteration";
    # check this too Jiyun
    # my $docs = $runDocs{$RUN}{$topic};
    # my $iters = $runIterations{$RUN}{$topic};

    push @{$runDocs{$RUN}{$topic}}, $docno;
    push @{$runIterations{$RUN}{$topic}}, $iteration;

    # print "@docs\n";
    # print "$iters\n";

    if(defined $doclength && length $doclength > 0){
       if(!exists $docLengthMap{$RUN}{$docno}){
        $docLengthMap{$RUN}{$docno} = $doclength;
       }
    } 
  }

  # use Data::Dumper;
  # print Dumper(%runDocs);
  # print Dumper(%runIterations);
  #########################################

  #### Process runs: compute measures for each topic and average

  # process each topic
  my %runTopics = %{$runDocs{$RUN}};
  foreach my $tid (keys %runTopics){

    # we don't need to do this anymore because we already store in
    # runDocs and runIterations

    # for ($i = 0; $i <= $#run; $i++) {
    #   ($topic, $docno, $score, $iteration) = split (' ', $run[$i]);

    #   # Jiyun, not sure if this is the best way to use local variables within each loop
    #   $docls[$#docls + 1] = $docno;
    #   $iterations[$#iterations + 1] = $iteration;
    # }

    # Jiyun, confirm this is correct syntax/optimal
    &topicDone ($RUN, $tid, \@{$runDocs{$RUN}{$tid}}, \@{$runIterations{$RUN}{$tid}});
    # $#docls = -1;
    # $#iterations = -1;

    &clearEnv;
  }

}

closedir(DIR);


exit 0;

#########################################

#### Compute and report information for current topic

sub topicDone {
  my ($runid, $topic, $ref_docls, $ref_iterations) = @_;
  if (exists $seen{$topic}) { #and $runid eq "multir" and $topic eq "DD15-52") {
    my $K = $maxIterations{$runid}{$topic};

    # my $_ct = &ct($K, $topic, $ref_docls, $ref_iterations);
    # my $_time = &getTime($K, $topic, $ref_docls, $ref_iterations);

    my $ct_accu = 0;
    my @tmp_docs = @{$ref_docls};
    my @tmp_iterations = @{$ref_iterations};
    my $lastIndex = $#tmp_docs + 1;
    # print "$lastIndex\n";
    #

    # compute gains (don't need to do it twice for ct and act)
    my $gains = ();
    my $ct_scores = ();

    $#gains = -1;
    $#ct_scores = -1;

    for($i = 0; $i < $lastIndex; $i++) {

      # let's calculate ct first
      $gains[$#gains + 1] = &getDocGain($topic, $tmp_docs[$i], $i + 1) / $MAX_HEIGHT;
      # print "$gains[$#gains]\n";
      if($#gains != 0) {
        # print "$#gains\n$gains[$#gains - 1]\n$gains[$#gains]\n";
        $gains[$#gains] = $gains[$#gains - 1] + $gains[$#gains]; # accumulate gains
        # print "$#gains\n$gains[$#gains - 1]\n$gains[$#gains]\n";
      }

      my $curIteration = $tmp_iterations[$i];
      my $nextIteration = $tmp_iterations[$i + 1];
      # &clearEnv;

      my $_time = &getTime($curIteration, $topic, $ref_docls, $ref_iterations);

      $ct_scores[$#ct_scores + 1] = $gains[$#gains] / $_time; 
      # print "@{$ct_scores}\n";
      if($#ct_scores != 0) {
        $ct_scores[$#ct_scores] = $ct_scores[$#ct_scores - 1] + $ct_scores[$#ct_scores]; # accumulate scores
      }
      #if ($curIteration == 1) {
      if ($lastIndex == ($i + 1) or $nextIteration > $curIteration) {
        my $ct_speed = 0;
        # print "$_time\n$#gains\n$gains[$#gains]\n";
        if($_time != 0){
            $ct_speed = $gains[$#gains] / $_time;
        }
        # don't need to check if docCount !=0 
        # because we're in the loop, docCount must be greater than 0
        # print "$ct_scores[$#ct_scores]\n";
        $ct_accu = $ct_scores[$#ct_scores] / ($i + 1); # $i + 1 because i is zero-based
        my $tid = substr($topic,5); # remove DD15-
        # print "@gains\n@ct_scores\n";

        # we've finished processing all docs up to current iteration
        printf  "$runid,$tid,$curIteration,%.10f,%.10f\n",$ct_speed,$ct_accu;
      }
    #}
    } 
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


#########################################

sub getDocGain{
  my ($topic, $docno, $rank) = @_;
  my $rel = 0;

  # print "@_\n";
  
  if(exists $qrels{$topic}{$docno}){
    my %subtopics = %{$qrels{$topic}{$docno}};
    my $inFlag = -1;
    my @ks = keys %subtopics;
    # print "$topic $docno\n";
    # print "@ks\n";
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
        } else {
          # print "$topic $subKey\n";
          # print "$currentGainHeight{$topic}{$subKey}\n";
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
  # print "@_\n$rel\n";
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
