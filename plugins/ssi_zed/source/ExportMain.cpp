#include "pch.h"
#include "ssized.h"
#include "base/Factory.h"

#ifndef DLLEXP
#define DLLEXP extern "C" __declspec(dllexport)
#endif

DLLEXP bool Register(ssi::Factory *factory, FILE *logfile, ssi::IMessage *message) {

    fprintf(stderr, "[ssi_zed] Register() called\n"); fflush(stderr);

    ssi::Factory::SetFactory(factory);
    fprintf(stderr, "[ssi_zed] SetFactory OK\n"); fflush(stderr);

    if (logfile) {
        ssiout = logfile;
    }
    if (message) {
        ssimsg = message;
    }

    bool result = true;

    fprintf(stderr, "[ssi_zed] registering ZedCamera...\n"); fflush(stderr);
    result = ssi::Factory::Register(ssi::ZedCamera::GetCreateName(), ssi::ZedCamera::Create) && result;
    fprintf(stderr, "[ssi_zed] ZedCamera result=%d\n", (int)result); fflush(stderr);

    result = ssi::Factory::Register(ssi::ZedSkeletonConverter::GetCreateName(), ssi::ZedSkeletonConverter::Create) && result;
    fprintf(stderr, "[ssi_zed] ZedSkeletonConverter result=%d\n", (int)result); fflush(stderr);

    return result;
}