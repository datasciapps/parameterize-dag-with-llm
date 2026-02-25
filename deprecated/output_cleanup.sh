echo "[Clean up script for output]"
echo "Current content in output/"
ls ./output
read -r -p "Are you really sure deleting ALL files listed above? (yes/No): " confirmation


if [[ "$confirmation" =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Confirmation received. Proceeding with deletion simulation..."
    
    # !!! DANGER ZONE !!!
    # This command uses 'echo' for safety. To ACTUALLY DELETE, replace the line below with:
    # rm "$TARGET_DIR"*
    rm ./output/*.log
    rm ./output/*.pdf
    rm ./output/*.json
    rm ./output/*.csv
    echo "Deleted, now ./output looking like"
    ls ./output

else
    echo "Deletion cancelled. No files were removed from $TARGET_DIR."
fi
