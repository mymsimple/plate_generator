echo "=================="
echo "=  图片增强"
echo "=================="

if [ "$2" = "" ]; then
    echo "Usage: enhance.sh <生成图片路径><生成标签文件路径> <增强后图片路径> <增强后图片标签路径>"
    exit
fi

nohup python -m main.image_enhance \
    --gen_path=data/plate/ \
    --gen_label=data/plate_txt/ \
    --enhance_path=data/enhance/ \
    --enhance_label=data/enhance_txt/ \
    >logs/enhance.log 2>&1 &