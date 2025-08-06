/**
 * @file   grt_static_rotation.c
 * @author Zhu Dengda (zhudengda@mail.iggcas.ac.cn)
 * @date   2025-04-08
 * 
 *    根据预先合成的静态位移空间导数，组合成静态旋转张量
 * 
 */


#include "common/const.h"

#include "grt.h"

/** 该子模块的参数控制结构体 */
typedef struct {
    char *name;
} GRT_MODULE_CTRL;

/** 释放结构体的内存 */
static void free_Ctrl(GRT_MODULE_CTRL *Ctrl){
    free(Ctrl->name);
    free(Ctrl);
}

/** 打印使用说明 */
static void print_help(){
printf("\n"
"[grt static rotation] %s\n\n", GRT_VERSION);printf(
"    Conbine spatial derivatives of static displacements (read from stdin)\n"
"    into rotation tensor. For example, \"ZR\" in filename means\n"
"    0.5*(u_{z,r} - u_{r,z}).\n"
"\n\n"
"Usage:\n"
"----------------------------------------------------------------\n"
"    grt static rotation < <file>\n"
"\n\n\n"
);
}


/** 从命令行中读取选项，处理后记录到全局变量中 */
static void getopt_from_command(GRT_MODULE_CTRL *Ctrl, int argc, char **argv){
    char* command = Ctrl->name;
    int opt;
    while ((opt = getopt(argc, argv, ":h")) != -1) {
        switch (opt) {
            GRT_Common_Options_in_Switch(command, (char)(optopt));
        }
    }

    // 暂不支持设置其它参数
}


/** 子模块主函数 */
int static_rotation_main(int argc, char **argv){
    GRT_MODULE_CTRL *Ctrl = calloc(1, sizeof(*Ctrl));
    Ctrl->name = strdup(argv[0]);
    const char *command = Ctrl->name;

    getopt_from_command(Ctrl, argc, argv);

    // 从标准输入中读取合成的静态位移及其空间导数
    double x0, y0, syn[3], syn_upar[3][3];  // [3][3]表示u_{i,j}

    // 建立一个指针数组，方便读取多列数据
    double *pt_grn[14];
    // 按照特定顺序
    {
        double **pt = &pt_grn[0];
        *(pt++) = &x0;
        *(pt++) = &y0;
        for(int k=0; k<3; ++k)  *(pt++) = &syn[k];
        for(int k=0; k<3; ++k){
            for(int i=0; i<3; ++i){
                *(pt++) = &syn_upar[i][k]; //  u_i / x_k
            }
        }
    }

    // 是否已打印输出的列名
    bool printHead = false;

    // 输入列数
    int ncols = 0;

    // 物性参数
    double src_va=0.0, src_vb=0.0, src_rho=0.0;
    double rcv_va=0.0, rcv_vb=0.0, rcv_rho=0.0;

    // 震中距
    double dist = 0.0;

    // 三分量
    const char *chs = NULL;

    // 输出分量格式，即是否需要旋转到ZNE
    bool rot2ZNE = false;

    // 逐行读入
    char line[1024];
    int iline = 0;
    while(fgets(line, sizeof(line), stdin)){
        iline++;
        if(iline == 1){
            // 读取震源物性参数
            if(3 != sscanf(line, "# %lf %lf %lf", &src_va, &src_vb, &src_rho)){
                GRTRaiseError("[%s] Error! Unable to read src property from \"%s\". \n", command, line);
            }
        }
        else if(iline == 2){
            // 读取场点物性参数
            if(3 != sscanf(line, "# %lf %lf %lf", &rcv_va, &rcv_vb, &rcv_rho)){
                GRTRaiseError("[%s] Error! Unable to read rcv property from \"%s\". \n", command, line);
            }
        }
        else if(iline == 3){
            // 根据列长度判断是否有位移空间导数
            char *copyline = strdup(line+1);  // +1去除首个#字符
            char *token = strtok(copyline, " ");
            while (token != NULL) {
                // 根据列名尾字符判断是否需要旋转到ZNE，出现一次即可
                if(!rot2ZNE && strlen(token) > 0 && token[strlen(token)-1]=='N')   rot2ZNE = true;
                ncols++;
                token = strtok(NULL, " ");
            }
            free(copyline);

            // 指示特定的通道名
            chs = (rot2ZNE)? ZNEchs : ZRTchs;

            // 想合成位移空间导数但输入的格林函数没有
            if(ncols < 14){
                GRTRaiseError("[%s] Error! The input has no spatial derivatives. \n", command);
            }
        }
        if(line[0] == '#')  continue;

        // 读取该行数据
        char *copyline = strdup(line);
        char *token = strtok(copyline, " ");
        for(int i=0; i<ncols; ++i){
            sscanf(token, "%lf", pt_grn[i]);  token = strtok(NULL, " ");
        }
        free(copyline);

        // 计算震中距
        dist = sqrt(x0*x0 + y0*y0);
        if(dist < 1e-5)  dist=1e-5;

        // 先输出列名
        if(!printHead){
            // 打印物性参数
            fprintf(stdout, "# "GRT_REAL_FMT" "GRT_REAL_FMT" "GRT_REAL_FMT"\n", src_va, src_vb, src_rho);
            fprintf(stdout, "# "GRT_REAL_FMT" "GRT_REAL_FMT" "GRT_REAL_FMT"\n", rcv_va, rcv_vb, rcv_rho);
            
            char XX[20];
            sprintf(XX, GRT_STRING_FMT, "X(km)"); XX[0]='#';
            fprintf(stdout, "%s", XX);
            fprintf(stdout, GRT_STRING_FMT, "Y(km)");
            char s_channel[15];
            for(int k=0; k<2; ++k){
                for(int i=k+1; i<3; ++i){
                    sprintf(s_channel, "%c%c", toupper(chs[k]), toupper(chs[i])); 
                    fprintf(stdout, GRT_STRING_FMT, s_channel);
                }
            }
            fprintf(stdout, "\n");
            printHead = true;
        }

        // 打印xy位置
        fprintf(stdout, GRT_REAL_FMT GRT_REAL_FMT, x0, y0);

        // 循环3个分量
        char c1, c2;
        for(int i1=0; i1<2; ++i1){
            c1 = chs[i1];
            for(int i2=i1+1; i2<3; ++i2){
                c2 = chs[i2];

                double val = 0.0;

                val = 0.5 * (syn_upar[i1][i2] - syn_upar[i2][i1]);

                // 特殊情况需加上协变导数，1e-5是因为km->cm
                if(c1=='R' && c2=='T'){
                    val -= 0.5 * syn[2] / dist * 1e-5;
                }

                // 打印结果
                fprintf(stdout, GRT_REAL_FMT, val);
            }
        }

        fprintf(stdout, "\n");
    }

    if(iline==0){
        GRTRaiseError("[%s] Error! Empty input. \n", command);
    }

    free_Ctrl(Ctrl);
    return EXIT_SUCCESS;
}