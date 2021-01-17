<style media="all">
.container
{
margin:0 auto;
padding:0;
width:100%;
overflow: hidden;
}

.left {float: left;}

.right {float: right;}

.left, .right
{
width:49%;
border:3px solid #00CD00;
padding:0;
font-family:Arial, Times, serif;
}

.contentleft h1, .contentright h1
{
margin:0;
padding:0;
display:block;
padding: 5px 0;
}

</style>

# PuzzleSkyPieces


Puzzles with large areas of sky can be demanding. This small script is intended to assist you by
 separating single pieces according to their blue-color gradient. Details are shown below.
 
### Requirements:
* [Pillow-8.1.0](https://pypi.org/project/Pillow/) Required for image processing

<div>
  <img style="vertical-align:middle" src="Images/example_scan.jpg" width="200px">
  <span style=""> </span>
</div>

<div class="container">
    <div class="left">
        <img style="vertical-align:middle" src="Images/example_scan.jpg" width="200px">
    </div>

    <div class="right">
        ### Input:
        A .jpg file (or any other file type supported by Pillow) that contains a scan of blue puzzle pieces.
        
        Note: to obtain good results, one should leave a small space between the single parts.
    </div>
</div>