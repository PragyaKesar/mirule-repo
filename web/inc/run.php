<?php
// Calls the Python back end without a shell.
// The command is passed to proc_open as an array, so the user's
// sequence is a single argument and can never be read as shell syntax.

function run_mirule(array $args) {
    $python = getenv('MIRULE_PYTHON') ?: (is_executable('/opt/venv/bin/python') ? '/opt/venv/bin/python' : 'python3');
    $root = getenv('MIRULE_ROOT') ?: (is_dir('/app/mirule') ? '/app' : dirname(__DIR__, 2));
    $cmd = array_merge([$python, '-m', 'mirule.predict'], array_map('strval', $args));
    $spec = [1 => ['pipe', 'w'], 2 => ['pipe', 'w']];
    $proc = proc_open($cmd, $spec, $pipes, $root);
    if (!is_resource($proc)) {
        return ['ok' => false, 'error' => 'The prediction service is unavailable.'];
    }
    $out = stream_get_contents($pipes[1]);
    $err = stream_get_contents($pipes[2]);
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($proc);
    $data = json_decode($out, true);
    if (!is_array($data)) {
        error_log('miRULE back end error: ' . $err);
        return ['ok' => false, 'error' => 'The prediction could not be completed.'];
    }
    return $data;
}

// First line of defence; Python validates again.
function read_sequence() {
    $raw = isset($_POST['sequence']) ? (string)$_POST['sequence'] : '';
    if (strlen($raw) > 5000) {
        return [null, 'The input is too long (5,000 characters at most).'];
    }
    $lines = preg_split('/\R/', $raw);
    $lines = array_filter($lines, function ($l) { return strpos(ltrim($l), '>') !== 0; });
    $seq = strtoupper(preg_replace('/\s+/', '', implode('', $lines)));
    if ($seq === '') {
        return [null, 'Please enter a sequence.'];
    }
    if (!preg_match('/^[ACGTU]+$/', $seq)) {
        return [null, 'The sequence may contain only A, C, G, U (or T).'];
    }
    return [$seq, null];
}
