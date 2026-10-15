param([Parameter(Mandatory=$true)][string]$VersionPath)
$ErrorActionPreference='Stop'
$report=Get-Content -LiteralPath (Join-Path $VersionPath 'project\jianying.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$source=(Join-Path $VersionPath $report.draft).Replace('/','\')
$name=Split-Path -Path $source -Leaf
if ($name -notmatch '^Douyin-[a-z0-9-]+-v[0-9]{3}$') { throw 'Unexpected task name' }
$draftRoot=Join-Path $env:LOCALAPPDATA 'JianyingPro\User Data\Projects\com.lveditor.draft'
$target=Join-Path $draftRoot $name
if (Test-Path -LiteralPath $target) { throw 'Existing draft is preserved; create a new video version.' }
if (-not (Test-Path -LiteralPath $draftRoot)) { throw 'Existing Jianying drafts root not found' }
if (Get-Process -Name JianyingPro -ErrorAction SilentlyContinue) { throw 'Jianying is running; preserve its open work and import when it is closed.' }
Copy-Item -LiteralPath $source -Destination $target -Recurse
$media=New-Item -ItemType Directory -Path (Join-Path $target 'media')
foreach ($item in (Get-ChildItem -LiteralPath (Join-Path $source 'materials') -File)) {
    $from=$item.FullName
    $to=Join-Path (Join-Path $target 'materials') $item.Name
    if ((Get-FileHash -LiteralPath $from).Hash -ne (Get-FileHash -LiteralPath $to).Hash) { throw 'Media hash mismatch' }
}
Copy-Item -LiteralPath (Join-Path $VersionPath 'thumbnail.png') -Destination (Join-Path $media.FullName 'cover.png')
$contentPath=Join-Path $target 'draft_info.json'
$content=Get-Content -LiteralPath $contentPath -Raw -Encoding UTF8
$old=(ConvertTo-Json -InputObject $source -Compress).Trim('"')
$new=(ConvertTo-Json -InputObject $target -Compress).Trim('"')
if (-not $content.Contains($old)) { throw 'Draft-local material references not found' }
$content=$content.Replace($old,$new)
[System.IO.File]::WriteAllText($contentPath,$content,(New-Object System.Text.UTF8Encoding($false)))
$metaPath=Join-Path $target 'draft_meta_info.json'
$meta=Get-Content -LiteralPath $metaPath -Raw -Encoding UTF8 | ConvertFrom-Json
$meta.draft_fold_path=$target
$meta.draft_root_path=$draftRoot
$meta.draft_cover=Join-Path $media.FullName 'cover.png'
$timestamp=[DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()*1000
$meta | Add-Member -NotePropertyName tm_draft_create -NotePropertyValue $timestamp -Force
$meta | Add-Member -NotePropertyName tm_draft_modified -NotePropertyValue $timestamp -Force
[System.IO.File]::WriteAllText($metaPath,($meta|ConvertTo-Json -Depth 100),(New-Object System.Text.UTF8Encoding($false)))
# Register only this new draft. Back up the existing index, retain every entry,
# and refuse concurrent changes. Never copy or modify an existing user draft.
$indexPath=Join-Path $draftRoot 'root_meta_info.json'
$before=Get-FileHash -LiteralPath $indexPath
$index=Get-Content -LiteralPath $indexPath -Raw -Encoding UTF8 | ConvertFrom-Json
$entry=($meta|ConvertTo-Json -Depth 100)|ConvertFrom-Json
$entry|Add-Member -NotePropertyName draft_json_file -NotePropertyValue $contentPath -Force
$index.all_draft_store=@($index.all_draft_store)+@($entry)
$private=New-Item -ItemType Directory -Path (Join-Path $VersionPath 'project\.private') -Force
$backup=Join-Path $private.FullName 'jianying-root-index-before.json'
Copy-Item -LiteralPath $indexPath -Destination $backup
if ((Get-FileHash -LiteralPath $indexPath).Hash -ne $before.Hash) { throw 'Draft index changed concurrently; index was not replaced' }
[System.IO.File]::WriteAllText($indexPath,($index|ConvertTo-Json -Depth 100),(New-Object System.Text.UTF8Encoding($false)))
$result=[ordered]@{imported=$true;draft_path=$target;name=$name;media_hashes_verified=$true;previous_draft_count=($index.all_draft_store.Count-1);open_verified=$false;export_verified=$false}
$json=$result|ConvertTo-Json
[System.IO.File]::WriteAllText((Join-Path $VersionPath 'evidence\windows-import.json'),$json,(New-Object System.Text.UTF8Encoding($false)))
Write-Output $json
