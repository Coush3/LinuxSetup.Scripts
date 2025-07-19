#!/bin/bash

# Function to display the main menu (categories)
main_menu() {
    clear
    echo "セットアップスクリプト メニュー"
    echo "============================="
    echo "カテゴリを選択してください:"

    # Find all subdirectories, excluding .git, and store them in an array
    mapfile -t categories < <(find . -maxdepth 1 -mindepth 1 -type d ! -name ".git" | sed 's|./||' | sort)

    if [ ${#categories[@]} -eq 0 ]; then
        echo "実行可能なカテゴリが見つかりません。"
        exit 1
    fi

    # Display categories using 'select'
    PS3="番号を選択してください (終了するにはq): "
    select category in "${categories[@]}"; do
        if [[ -n "$category" ]]; then
            script_menu "$category"
            # After returning from script_menu, break to redisplay the main menu
            break
        elif [[ "$REPLY" == "q" ]]; then
            echo "終了します。"
            exit 0
        else
            echo "無効な選択です: $REPLY"
        fi
    done
}

# Function to display the script menu for a given category
script_menu() {
    local category_dir=$1
    clear
    echo "カテゴリ: $category_dir"
    echo "============================="
    echo "実行するスクリプトを選択してください:"

    # Find all .sh files in the selected directory
    mapfile -t scripts < <(find "$category_dir" -maxdepth 1 -name "*.sh" -printf "%f\n" | sort)

    if [ ${#scripts[@]} -eq 0 ]; then
        echo "このカテゴリには実行可能なスクリプトがありません。"
        read -p "メインメニューに戻るにはEnterキーを押してください..."
        return
    fi

    # Display scripts using 'select'
    PS3="番号を選択してください (メインメニューに戻るにはq): "
    select script in "${scripts[@]}"; do
        if [[ -n "$script" ]]; then
            local script_path="$category_dir/$script"
            if [ -f "$script_path" ]; then
                clear
                echo "実行中: $script_path"
                echo "------------------------------------------------------------"
                # Make sure the script is executable and run it
                bash "$script_path"
                echo "------------------------------------------------------------"
                read -p "スクリプトが完了しました。続けるにはEnterキーを押してください..."
                # Break to go back to the caller (main_menu)
                break
            else
                echo "エラー: スクリプトファイルが見つかりません: $script_path"
            fi
        elif [[ "$REPLY" == "q" ]]; then
            # Break to go back to the main menu
            break
        else
            echo "無効な選択です: $REPLY"
        fi
    done
}

# Main loop to keep the menu running
while true; do
    main_menu
done
