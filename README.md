ex:
```
./betterstack_cli.py --from-date="2024-10-10" \
| jq '[ 
    .[] 
    | select(.attributes.status != "Resolved") 
    | . 
] 
| sort_by(.attributes.status) 
| map({
    name: .attributes.name,
    started_at: .attributes.started_at,
    acknowledged_at: .attributes.acknowledged_at,
    acknowledged_by: .attributes.acknowledged_by
})
'
```
