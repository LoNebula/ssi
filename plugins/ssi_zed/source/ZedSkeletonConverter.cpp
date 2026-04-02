#include "pch.h"
#include "ZedSkeletonConverter.h"

namespace ssi {

ZedSkeletonConverter::ZedSkeletonConverter(const ssi_char_t* file)
    : _file(0) {
    if (file) {
        if (!OptionList::LoadXML(file, &_options)) {
            OptionList::SaveXML(file, &_options);
        }
        _file = ssi_strcpy(file);
    }
}

ZedSkeletonConverter::~ZedSkeletonConverter() {
    if (_file) {
        OptionList::SaveXML(_file, &_options);
        delete[] _file;
    }
}

void ZedSkeletonConverter::transform_enter(ssi_stream_t& stream_in, ssi_stream_t& stream_out,
    ssi_size_t xtra_stream_in_num, ssi_stream_t xtra_stream_in[]) {
}

void ZedSkeletonConverter::transform(ITransformer::info info,
    ssi_stream_t& stream_in, ssi_stream_t& stream_out,
    ssi_size_t xtra_stream_in_num, ssi_stream_t xtra_stream_in[]) {

    const ZED_SKELETON* srcptr = ssi_pcast(const ZED_SKELETON, stream_in.ptr);
    SSI_SKELETON* dstptr = ssi_pcast(SSI_SKELETON, stream_out.ptr);

    for (ssi_size_t s = 0; s < stream_in.num * _options.n_skeletons; s++) {
        // Zero-initialise output skeleton
        for (ssi_size_t i = 0; i < SSI_SKELETON_JOINT::NUM; i++) {
            for (ssi_size_t j = 0; j < SSI_SKELETON_JOINT_VALUE::NUM; j++) {
                (*dstptr)[i][j] = SSI_SKELETON_INVALID_JOINT_VALUE;
            }
        }
        convertZed(*srcptr, *dstptr);
        srcptr++;
        dstptr++;
    }
}

void ZedSkeletonConverter::transform_flush(ssi_stream_t& stream_in, ssi_stream_t& stream_out,
    ssi_size_t xtra_stream_in_num, ssi_stream_t xtra_stream_in[]) {
}

void ZedSkeletonConverter::convertZed(const ZED_SKELETON& from, SSI_SKELETON& to) {
    copyJoint(to, SSI_SKELETON_JOINT::HEAD,           from, ZED_JOINT::HEAD);
    copyJoint(to, SSI_SKELETON_JOINT::NECK,           from, ZED_JOINT::NECK);
    copyJoint(to, SSI_SKELETON_JOINT::TORSO,          from, ZED_JOINT::CHEST_SPINE);
    copyJoint(to, SSI_SKELETON_JOINT::WAIST,          from, ZED_JOINT::PELVIS);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_SHOULDER,  from, ZED_JOINT::LEFT_SHOULDER);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_ELBOW,     from, ZED_JOINT::LEFT_ELBOW);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_WRIST,     from, ZED_JOINT::LEFT_WRIST);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_HAND,      from, ZED_JOINT::LEFT_HAND);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_SHOULDER, from, ZED_JOINT::RIGHT_SHOULDER);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_ELBOW,    from, ZED_JOINT::RIGHT_ELBOW);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_WRIST,    from, ZED_JOINT::RIGHT_WRIST);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_HAND,     from, ZED_JOINT::RIGHT_HAND);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_HIP,       from, ZED_JOINT::LEFT_HIP);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_KNEE,      from, ZED_JOINT::LEFT_KNEE);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_ANKLE,     from, ZED_JOINT::LEFT_ANKLE);
    copyJoint(to, SSI_SKELETON_JOINT::LEFT_FOOT,      from, ZED_JOINT::LEFT_FOOT);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_HIP,      from, ZED_JOINT::RIGHT_HIP);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_KNEE,     from, ZED_JOINT::RIGHT_KNEE);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_ANKLE,    from, ZED_JOINT::RIGHT_ANKLE);
    copyJoint(to, SSI_SKELETON_JOINT::RIGHT_FOOT,     from, ZED_JOINT::RIGHT_FOOT);
    copyJoint(to, SSI_SKELETON_JOINT::FACE_NOSE,      from, ZED_JOINT::NOSE);
    copyJoint(to, SSI_SKELETON_JOINT::FACE_LEFT_EAR,  from, ZED_JOINT::LEFT_EAR);
    copyJoint(to, SSI_SKELETON_JOINT::FACE_RIGHT_EAR, from, ZED_JOINT::RIGHT_EAR);
    // FACE_FOREHEAD and FACE_CHIN have no ZED equivalent — left as invalid
}

} // namespace ssi
