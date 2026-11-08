param([string]$Docx)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
try {
    $d = $w.Documents.Open($Docx)
    $d.Fields.Update() | Out-Null
    foreach ($t in $d.TablesOfContents) { $t.Update() }
    $d.Save()
    $pdf = [IO.Path]::ChangeExtension($Docx, '.pdf')
    $d.ExportAsFixedFormat($pdf, 17)
    "pages: " + $d.ComputeStatistics(2)
    $d.Close()
} finally { $w.Quit() }
