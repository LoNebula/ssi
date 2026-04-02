#pragma once

#ifndef SSI_ZED_SKELETON_CONVERTER_H
#define SSI_ZED_SKELETON_CONVERTER_H

#include "base/IFilter.h"
#include "ioput/option/OptionList.h"
#include "SSI_SkeletonCons.h"

namespace ssi {

// Converts the ZED BODY_34 skeleton stream (34 joints x XYZ float, meters,
// RIGHT_HANDED_Y_UP) into the SSI skeleton format (25 joints x 14 values, mm)
// so that SkeletonPainter can consume it directly.
class ZedSkeletonConverter : public IFilter {

public:

    class Options : public OptionList {
    public:
        Options() : n_skeletons(1) {
            addOption("numskel", &n_skeletons, 1, SSI_SIZE, "number of skeletons tracked");
        }
        ssi_size_t n_skeletons;
    };

public:
    static const ssi_char_t* GetCreateName() { return "ZedSkeletonConverter"; }
    static IObject* Create(const ssi_char_t* file) { return new ZedSkeletonConverter(file); }
    ~ZedSkeletonConverter();

    ZedSkeletonConverter::Options* getOptions() { return &_options; }
    const ssi_char_t* getName() { return GetCreateName(); }
    const ssi_char_t* getInfo() { return "Converts ZED BODY_34 skeleton stream to SSI skeleton format."; }

    void transform_enter(ssi_stream_t& stream_in, ssi_stream_t& stream_out,
        ssi_size_t xtra_stream_in_num = 0, ssi_stream_t xtra_stream_in[] = 0);
    void transform(ITransformer::info info, ssi_stream_t& stream_in, ssi_stream_t& stream_out,
        ssi_size_t xtra_stream_in_num = 0, ssi_stream_t xtra_stream_in[] = 0);
    void transform_flush(ssi_stream_t& stream_in, ssi_stream_t& stream_out,
        ssi_size_t xtra_stream_in_num = 0, ssi_stream_t xtra_stream_in[] = 0);

    ssi_size_t getSampleDimensionOut(ssi_size_t sample_dimension_in) {
        return _options.n_skeletons * SSI_SKELETON_JOINT::NUM * SSI_SKELETON_JOINT_VALUE::NUM;
    }
    ssi_size_t getSampleBytesOut(ssi_size_t sample_bytes_in) {
        return SSI_SKELETON_VALUE_BYTES;
    }
    ssi_type_t getSampleTypeOut(ssi_type_t sample_type_in) {
        return SSI_SKELETON_VALUE_SSITYPE;
    }

    const void* getMetaData(ssi_size_t& size) {
        _meta_out = ssi_skeleton_meta(SSI_SKELETON_TYPE::SSI, _options.n_skeletons);
        size = sizeof(_meta_out);
        return &_meta_out;
    }

    // ZED BODY_34 joint indices
    struct ZED_JOINT {
        enum List {
            PELVIS       = 0,
            NAVAL_SPINE  = 1,
            CHEST_SPINE  = 2,
            NECK         = 3,
            LEFT_CLAVICLE   = 4,
            LEFT_SHOULDER   = 5,
            LEFT_ELBOW      = 6,
            LEFT_WRIST      = 7,
            LEFT_HAND       = 8,
            LEFT_HANDTIP    = 9,
            LEFT_THUMB      = 10,
            RIGHT_CLAVICLE  = 11,
            RIGHT_SHOULDER  = 12,
            RIGHT_ELBOW     = 13,
            RIGHT_WRIST     = 14,
            RIGHT_HAND      = 15,
            RIGHT_HANDTIP   = 16,
            RIGHT_THUMB     = 17,
            LEFT_HIP        = 18,
            LEFT_KNEE       = 19,
            LEFT_ANKLE      = 20,
            LEFT_FOOT       = 21,
            RIGHT_HIP       = 22,
            RIGHT_KNEE      = 23,
            RIGHT_ANKLE     = 24,
            RIGHT_FOOT      = 25,
            HEAD            = 26,
            NOSE            = 27,
            LEFT_EYE        = 28,
            LEFT_EAR        = 29,
            RIGHT_EYE       = 30,
            RIGHT_EAR       = 31,
            LEFT_HEEL       = 32,
            RIGHT_HEEL      = 33,
            COUNT           = 34
        };
    };

protected:
    ZedSkeletonConverter(const ssi_char_t* file = 0);
    ZedSkeletonConverter::Options _options;
    ssi_char_t* _file;
    SSI_SKELETON_META _meta_out;

    // Input layout: float[34][3] (X, Y, Z per joint, meters)
    typedef float ZED_SKELETON[ZED_JOINT::COUNT][3];

    void convertZed(const ZED_SKELETON& from, SSI_SKELETON& to);

    inline void copyJoint(SSI_SKELETON& to, SSI_SKELETON_JOINT::List ssi_j,
                          const ZED_SKELETON& from, int zed_j) {
        // ZED: meters, RIGHT_HANDED_Y_UP  →  SSI: mm, Y-up (no inversion needed)
        to[ssi_j][SSI_SKELETON_JOINT_VALUE::POS_X] = from[zed_j][0] * 1000.0f;
        to[ssi_j][SSI_SKELETON_JOINT_VALUE::POS_Y] = from[zed_j][1] * 1000.0f;
        to[ssi_j][SSI_SKELETON_JOINT_VALUE::POS_Z] = from[zed_j][2] * 1000.0f;
        // Confidence: treat non-zero position as valid (1.0), zero as invalid (0.0)
        bool valid = (from[zed_j][0] != 0.0f || from[zed_j][1] != 0.0f || from[zed_j][2] != 0.0f);
        to[ssi_j][SSI_SKELETON_JOINT_VALUE::POS_CONF] = valid ? 1.0f : 0.0f;
        // Rotations not available from ZED position-only stream — leave as invalid (0.0f)
    }
};

} // namespace ssi

#endif
