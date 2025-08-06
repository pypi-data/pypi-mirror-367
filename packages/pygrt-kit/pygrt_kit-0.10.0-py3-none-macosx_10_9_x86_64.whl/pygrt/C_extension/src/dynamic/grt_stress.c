/**
 * @file   grt_strain.c
 * @author Zhu Dengda (zhudengda@mail.iggcas.ac.cn)
 * @date   2025-03-28
 * 
 *    根据预先合成的位移空间导数，组合成应力张量（由于有衰减，须在频域内进行）
 * 
 */

#include <complex.h>
#include <fftw3.h>

#include "common/attenuation.h"
#include "common/sacio2.h"
#include "common/const.h"

#include "grt.h"

/** 该子模块的参数控制结构体 */
typedef struct {
    char *name;
    char *s_dirpath;
    char *s_prefix;
    char *s_synpath;
} GRT_MODULE_CTRL;


/** 释放结构体的内存 */
static void free_Ctrl(GRT_MODULE_CTRL *Ctrl){
    free(Ctrl->name);
    free(Ctrl->s_dirpath);
    free(Ctrl->s_prefix);
    free(Ctrl->s_synpath);
    free(Ctrl);
}


/** 打印使用说明 */
static void print_help(){
printf("\n"
"[grt stress] %s\n\n", GRT_VERSION);printf(
"    Conbine spatial derivatives of displacements into stress tensor.\n"
"    (unit: dyne/cm^2 = 0.1 Pa)\n"
"\n\n"
"Usage:\n"
"----------------------------------------------------------------\n"
"    grt stress <syn_dir>/<name>\n"
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

    // 检查必选项有没有设置
    GRTCheckOptionSet(command, argc > 1);
}


int stress_main(int argc, char **argv){
    GRT_MODULE_CTRL *Ctrl = calloc(1, sizeof(*Ctrl));
    Ctrl->name = strdup(argv[0]);
    Ctrl->s_dirpath = strdup(argv[1]);
    
    const char *command = Ctrl->name;

    getopt_from_command(Ctrl, argc, argv);

    
    // 合成地震图目录路径
    Ctrl->s_synpath = (char*)malloc(sizeof(char)*(strlen(Ctrl->s_dirpath)+1));
    // 保存文件前缀 
    Ctrl->s_prefix  = (char*)malloc(sizeof(char)*(strlen(Ctrl->s_dirpath)+1));
    if(2 != sscanf(Ctrl->s_dirpath, "%[^/]/%s", Ctrl->s_synpath, Ctrl->s_prefix)){
        GRTRaiseError("[%s] " BOLD_RED "Error format in \"%s\".\n" DEFAULT_RESTORE, command, Ctrl->s_dirpath);
    }

    // 检查是否存在该目录
    GRTCheckDirExist(command, Ctrl->s_synpath);


    // ----------------------------------------------------------------------------------
    // 开始读取计算，输出6个量
    char c1, c2;
    char *s_filepath = (char*)malloc(sizeof(char) * (strlen(Ctrl->s_synpath)+strlen(Ctrl->s_prefix)+100));

    // 输出分量格式，即是否需要旋转到ZNE
    bool rot2ZNE = false;
    // 三分量
    const char *chs = NULL;

    // 判断标志性文件是否存在，来判断输出使用ZNE还是ZRT
    sprintf(s_filepath, "%s/n%sN.sac", Ctrl->s_synpath, Ctrl->s_prefix);
    rot2ZNE = (access(s_filepath, F_OK) == 0);

    // 指示特定的通道名
    chs = (rot2ZNE)? ZNEchs : ZRTchs;


    // 读取一个头段变量，获得基本参数，分配数组内存
    SACHEAD hd;
    sprintf(s_filepath, "%s/%c%s%c.sac", Ctrl->s_synpath, tolower(chs[0]), Ctrl->s_prefix, chs[0]);
    read_SAC_HEAD(command, s_filepath, &hd);
    int npts=hd.npts;
    float dt=hd.delta;
    float dist=hd.dist;
    float df=1.0/(npts*dt);
    int nf=npts/2 + 1;
    float va=hd.user1;
    float vb=hd.user2;
    float rho=hd.user3;
    float Qainv=hd.user4;
    float Qbinv=hd.user5;
    if(va <= 0.0 || vb < 0.0 || rho <= 0.0){
        fprintf(stderr, "[%s] " BOLD_RED "Error! Bad rcv_va, rcv_vb or rcv_rho in \"%s\" header.\n" DEFAULT_RESTORE, command, s_filepath);
        exit(EXIT_FAILURE);
    }
    // 申请内存
    // lamda * 体积应变
    fftwf_complex *lam_ukk = (fftwf_complex*)fftwf_malloc(sizeof(fftwf_complex)*nf);
    // 不同频率的lambda和mu
    fftwf_complex *lams = (fftwf_complex*)fftwf_malloc(sizeof(fftwf_complex)*nf);
    fftwf_complex *mus = (fftwf_complex*)fftwf_malloc(sizeof(fftwf_complex)*nf);
    // 分配FFTW数组
    fftwf_complex *carrin = (fftwf_complex*)fftwf_malloc(sizeof(fftwf_complex)*nf);
    fftwf_complex *carrout = (fftwf_complex*)fftwf_malloc(sizeof(fftwf_complex)*nf);
    float *arrin = (float*)malloc(sizeof(float)*npts);
    float *arrout = (float*)malloc(sizeof(float)*npts);
    fftwf_plan plan = fftwf_plan_dft_r2c_1d(npts, arrin, carrin, FFTW_ESTIMATE);
    fftwf_plan plan_inv = fftwf_plan_dft_c2r_1d(npts, carrout, arrout, FFTW_ESTIMATE);
    // 初始化
    for(int i=0; i<nf; ++i){
        lam_ukk[i] = lams[i] = mus[i] = carrin[i] = carrout[i] = 0.0f + I*0.0f;
    }
    for(int i=0; i<npts; ++i){
        arrin[i] = arrout[i] = 0.0f;
    }
    // 计算不同频率下的拉梅系数
    for(int i=0; i<nf; ++i){
        float freq, w;
        freq = (i==0) ? 0.01f : df*i; // 计算衰减因子不能为0频
        w = PI2 * freq;
        fftwf_complex atta, attb;
        atta = attenuation_law(Qainv, w);
        attb = attenuation_law(Qbinv, w);
        // 乘上1e10，转为dyne/(cm^2)
        mus[i] = vb*vb*attb*attb*rho*1e10;
        lams[i] = va*va*atta*atta*rho*1e10 - 2.0*mus[i];
    }

    // ----------------------------------------------------------------------------------
    // 先计算体积应变u_kk = u_11 + u22 + u33 和 lamda的乘积
    for(int i1=0; i1<3; ++i1){
        c1 = chs[i1];

        // 读取数据 u_{k,k}
        sprintf(s_filepath, "%s/%c%s%c.sac", Ctrl->s_synpath, tolower(c1), Ctrl->s_prefix, c1);
        arrin = read_SAC(command, s_filepath, &hd, arrin);

        // 累加
        fftwf_execute(plan);
        for(int i=0; i<nf; ++i)  lam_ukk[i] += carrin[i];
    }
    // 加上协变导数
    if(!rot2ZNE){
        sprintf(s_filepath, "%s/%sR.sac", Ctrl->s_synpath, Ctrl->s_prefix);
        arrin = read_SAC(command, s_filepath, &hd, arrin);
        fftwf_execute(plan);
        for(int i=0; i<nf; ++i)  lam_ukk[i] += carrin[i]/dist*1e-5;
    }

    // 乘上lambda系数
    for(int i=0; i<nf; ++i)  lam_ukk[i] *= lams[i];

    // 重新初始化
    for(int i=0; i<nf; ++i){
        carrin[i] = carrout[i] = 0.0f + I*0.0f;
    }
    for(int i=0; i<npts; ++i){
        arrin[i] = arrout[i] = 0.0f;
    }

    // ----------------------------------------------------------------------------------
    // 循环6个分量
    for(int i1=0; i1<3; ++i1){
        c1 = chs[i1];
        for(int i2=i1; i2<3; ++i2){
            c2 = chs[i2];

            // 读取数据 u_{i,j}
            sprintf(s_filepath, "%s/%c%s%c.sac", Ctrl->s_synpath, tolower(c2), Ctrl->s_prefix, c1);
            arrin = read_SAC(command, s_filepath, &hd, arrin);

            // 累加
            fftwf_execute(plan);
            for(int i=0; i<nf; ++i)  carrout[i] += carrin[i];

            // 读取数据 u_{j,i}
            sprintf(s_filepath, "%s/%c%s%c.sac", Ctrl->s_synpath, tolower(c1), Ctrl->s_prefix, c2);
            arrin = read_SAC(command, s_filepath, &hd, arrin);
            
            // 累加
            fftwf_execute(plan);
            for(int i=0; i<nf; ++i)  carrout[i] = (carrout[i] + carrin[i]) * mus[i];

            // 对于对角线分量，需加上lambda * u_kk
            if(c1 == c2){
                for(int i=0; i<nf; ++i)  carrout[i] += lam_ukk[i];
            }

            // 特殊情况需加上协变导数，1e-5是因为km->cm
            if(c1=='R' && c2=='T'){
                // 读取数据 u_T
                sprintf(s_filepath, "%s/%sT.sac", Ctrl->s_synpath, Ctrl->s_prefix);
                arrin = read_SAC(command, s_filepath, &hd, arrin);
                fftwf_execute(plan);
                for(int i=0; i<nf; ++i)  carrout[i] -= mus[i] * carrin[i] / dist * 1e-5;
            }
            else if(c1=='T' && c2=='T'){
                // 读取数据 u_R
                sprintf(s_filepath, "%s/%sR.sac", Ctrl->s_synpath, Ctrl->s_prefix);
                arrin = read_SAC(command, s_filepath, &hd, arrin);
                fftwf_execute(plan);
                for(int i=0; i<nf; ++i)  carrout[i] += 2.0f * mus[i] * carrin[i] / dist * 1e-5;
            }
            
            // 保存到SAC
            fftwf_execute(plan_inv);
            for(int i=0; i<npts; ++i)  arrout[i] /= npts;
            sprintf(hd.kcmpnm, "%c%c", c1, c2);
            sprintf(s_filepath, "%s/%s.stress.%c%c.sac", Ctrl->s_synpath, Ctrl->s_prefix, c1, c2);
            write_sac(s_filepath, hd, arrout);

            // 置零
            for(int i=0; i<nf; ++i)  carrout[i] = 0.0f + I*0.0f;
        }
    }


    if(arrin)  free(arrin);
    if(arrout)  free(arrout);

    if(lam_ukk)  fftwf_free(lam_ukk);
    if(lams)  fftwf_free(lams);
    if(mus)   fftwf_free(mus);
    if(carrin)  fftwf_free(carrin);
    if(carrout)  fftwf_free(carrout);

    fftwf_destroy_plan(plan);
    fftwf_destroy_plan(plan_inv);


    free_Ctrl(Ctrl);
    return EXIT_SUCCESS;
}