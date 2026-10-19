<?php
require __DIR__ . '/inc/layout.php';
page_header('Help', 'Help');
?>
<h2>Help</h2>
<h3>Input</h3>
<p>Paste one sequence. RNA (A, C, G, U) and DNA (A, C, G, T) are both accepted. T is read as U.
Spaces and line breaks are ignored. A FASTA header line starting with "&gt;" is removed.
Any other character is rejected.</p>
<table class="result compact">
  <tr><th>Analysis</th><th>Accepted length</th></tr>
  <tr><td>Precursor prediction</td><td>40 to 600 nt</td></tr>
  <tr><td>Mature miRNA identification</td><td>60 to 600 nt</td></tr>
  <tr><td>Precursor from primary sequence</td><td>100 to 1,500 nt</td></tr>
</table>
<h3>Output</h3>
<p><b>Probability of real pre-miRNA.</b> The support vector machine probability that the input
is a real plant pre-miRNA. Values of 0.5 or above are reported as real pre-miRNAs.</p>
<p><b>MFE and ensemble free energy.</b> RNAfold minimum free energy and ensemble free energy
at 37 °C, in kcal/mol.</p>
<p><b>MFE index 1.</b> MFE divided by GC content (%). In the training data, real pre-miRNAs have slightly more negative values than pseudo hairpins (medians −1.33 and −1.25).</p>
<p><b>Mature miRNA.</b> The locator predicts the 5′ start of the mature miRNA. A 21 nt sequence is
shown from that start, since most plant miRNAs are 21 nt. This module is experimental: the top
start is within 2 nt of an annotated mature in 16% of held-out precursors. Treat all three
candidates as hypotheses.</p>
<p><b>Primary sequence scan.</b> Windows are scored independently. Overlapping windows are merged so that
each reported window covers a different region.</p>
<h3>Limitations</h3>
<ul>
  <li>The models were trained on plant sequences only.</li>
  <li>Predictions use the single RNAfold MFE structure. Alternative structures are not considered.</li>
  <li>A high probability supports, but does not replace, expression evidence such as small RNA sequencing.</li>
</ul>
<?php page_footer(); ?>
