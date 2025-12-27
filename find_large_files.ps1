Get-ChildItem -Path C:\ -File -Recurse -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending |
    Select-Object -First 20 |
    ForEach-Object {
        [PSCustomObject]@{
            'Size(GB)' = [math]::Round($_.Length/1GB, 2)
            Path = $_.FullName
        }
    } | Format-Table -Wrap
