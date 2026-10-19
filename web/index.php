<?php
require __DIR__ . '/inc/layout.php';
page_header('Home', 'Home');
?>
<h2>Welcome to the miRULE webserver</h2>
<p>miRULE predicts plant microRNA precursors and their mature miRNAs from sequence alone.
It offers three analyses.</p>
<ul class="tools">
  <li><a href="precursor.php"><b>Precursor prediction.</b></a> Classifies an input hairpin as a real plant pre-miRNA or a pseudo hairpin.</li>
  <li><a href="mature.php"><b>Mature miRNA identification.</b></a> Locates the most probable mature miRNA within a predicted precursor.</li>
  <li><a href="primary.php"><b>Precursor from primary sequence.</b></a> Scans a longer primary transcript and reports the windows most likely to be pre-miRNAs.</li>
</ul>
<h3>Method</h3>
<p>Secondary structures and free energies are computed with RNAfold from the ViennaRNA Package.
The precursor classifier is a support vector machine trained on 5,680 unique plant sequences
(3,064 real pre-miRNAs and 2,616 pseudo hairpins). It uses 39 sequence, structure and
thermodynamic features. The mature miRNA locator is an experimental gradient boosting model
that scores every candidate start by nucleotide identity, base pairing state and position
relative to the terminal loop.</p>
<h3>Performance</h3>
<table class="result compact">
  <tr><th>Evaluation</th><th>Accuracy</th><th>AUC</th></tr>
  <tr><td>Precursor, 5 fold cross validation</td><td>98.0%</td><td>0.997</td></tr>
  <tr><td>Precursor, independent test set (71 sequences)</td><td>88.7%</td><td>0.938</td></tr>
  <tr><td>Mature start site, held out precursors (exact / within 2 nt)</td><td colspan="2">7.0% / 15.8%</td></tr>
</table>
<p class="note">See the Help page for details on inputs, outputs and interpretation.</p>
<?php page_footer(); ?>
