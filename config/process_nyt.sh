# uncompress and transform the NYT corpus data into TRECTEXT
# Copyright 2017 @ Georgetown University
# usage: process_nyt.sh [nyt corpus tgz file] [destination directory]

usage="usage: process_nyt.sh [path to input file] [path to output directory]"

if [ $# -ne 2 ]; then
    echo $usage
    exit 1
fi

SOURCE=$1
DEST=$2

build_DEST_direc(){
	# build DEST directory
        
	if [ -d $DEST ];then
		if [ -d $DEST/nyt_corpus ]; then
			rm -rf $DEST/nyt_corpus
		fi
		if [ -d $DEST/nyt_trectext ]; then
			rm -rf $DEST/nyt_trectext
		fi
		
		mkdir $DEST/nyt_trectext
		
		if [ -e $DEST/filelist ]; then
			rm -f $DEST/filelist
		fi
	else
                mkdir -p  $DEST/nyt_trectext
        fi
	
}

uncompress(){ # uncompress tgz file, remove the orginal file after uncompressing
	file=$1
	direc=$2
	if [[ ${file##*.} = "tgz" ]]; then
                echo tar -xzf $1 -C $direc
                tar -xzf $file -C $direc
                rm -f $file
	fi
}

xml2trectext(){
	file=$1

	echo transforming $file
	# transform xml to trectext
	if [[ ${file##*.} = "xml" ]]; then
		dest_file=$(basename $file)
		docno="${dest_file%.*}"
		dest_file=$DEST/nyt_trectext/$docno
		
		echo "<DOC>" > $dest_file
		echo "<DOCNO>"$docno"</DOCNO>" >> $dest_file
		echo "<TEXT>" >> $dest_file
		cat  $file >> $dest_file
		echo "</TEXT>" >> $dest_file
		echo "</DOC>" >> $dest_file
	fi 
}

walk_down(){
	direc=$1
        for file in $direc/*
        do
                uncompress $file $direc
        done
        for file in $direc/*
        do
                if [ -d $file ]; then
                        walk_down $file
                else
                        xml2trectext $file
                fi
        done
}

main(){
	echo build $DEST directory
	build_DEST_direc
	
	# uncompress
 	echo uncompressing...
	
 	# put nyt_corpus in destination directory	
	echo tar -xzf $SOURCE -C $DEST
	tar -xzf $SOURCE -C $DEST 


	# uncompress $DEST/nyt_corpus/data recursively

	# seems to be bug in linux, a redundant folder nyt_corpus/data/1987/01 is generated during uncompression
	# this problem is not found on mac OS
	if [ -d $DEST/nyt_corpus/data/1987/01 ]; then
        	echo removing redundant folder nyt_corpus/data/1987/01
        	rm -rf $DEST/nyt_corpus/data/1987/01
	fi
	
	walk_down $DEST/nyt_corpus/data

}

main

