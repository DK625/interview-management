import { DatePicker, Form, Input, Modal, Select, TimePicker } from "antd";
import { useAppDispatch, useAppSelector, useAuth } from "@/redux/hooks.ts";
import { useMemo } from "react";
import { InterviewStatus, OfferPosition } from "@/configs/constants.tsx";
import { createInterview, getInterviews, updateInterview } from "@/redux/features/interviewSlice.ts";
import { createCandidate, getCandidates, updateCandidate } from "@/redux/features/candidateSlice.ts";
import moment from "moment";
import { useState, useEffect } from "react";

export const ModalAddInterview = (props: any) => {
  const { role } = useAuth();
  const { initialValues, handleClose, isOpen } = props;
  const jobs = useAppSelector((state) => state.job.jobs);
  const candidates = useAppSelector((state) => state.candidate.candidates);
  const users = useAppSelector((state) => state.user.users);
  const userOptions = useMemo(() => users?.filter(it => it.role !== "Interviewer").map((user) => ({ label: user.username, value: user.id })), [users]);
  const candidateOptions = useMemo(() => candidates?.map((candidate) => ({
    label: `${candidate.full_name} (${candidate.email})`,
    value: candidate.id
  })), [candidates]);
  const [filteredCandidates, setFilteredCandidates] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [selectedCandidateId, setSelectedCandidateId] = useState(null);
  const [filteredUsers, setFilteredUsers] = useState([]);


  const isDisable = ["Passed", "Failed", "Cancelled"].includes(initialValues?.status) && role !== "Admin"

  // Cập nhật khi select candidate hoặc khi edit
  useEffect(() => {
    if (initialValues) {
      setSelectedCandidateId(initialValues.candidate_id);
    }
  }, [initialValues]);


  // Thêm useEffect để lọc candidates khi job thay đổi
  useEffect(() => {
    if (selectedJob) {
      const selectedJobData = jobs.find(job => job.id === selectedJob);
      if (selectedJobData) {
        const filteredUsersList = users
          .filter(user =>
            user.role !== "Interviewer" &&
            user.department?.toLowerCase() === selectedJobData.department?.toLowerCase()
          )
          .map(user => ({
            label: user.username,
            value: user.id
          }));
        setFilteredUsers(filteredUsersList);
      }
      console.log('selectedJobData: ', selectedJobData)
      console.log('filteredUsersList: ', users)
      const job = jobs.find(job => job.id === selectedJob);
      if (job) {
        const filtered = candidates.filter(candidate =>
          candidate.position?.toLowerCase() === job.position?.toLowerCase()
          && candidate.status == 'Waiting for interview'
        );
        console.log('candidates: ', candidates)

        setFilteredCandidates(filtered.map(candidate => ({
          label: `${candidate.full_name} (${candidate.email})`,
          value: candidate.id
        })));
      } else {
        setFilteredUsers([]);
        setFilteredCandidates([]);
      }
    }
  }, [selectedJob, users, jobs]);


  const jobOptions = useMemo(() => {
    const filteredJobs = jobs.filter(job => job.status === 'Open');

    return filteredJobs.map((job) => ({
      label: job.title + "-JOB" + job.id,
      value: job.id
    }));
  }, [jobs]);

  const positionOptions = OfferPosition.map((position) => ({ label: position, value: position }));
  const statusOptions = [
    { value: 'Invited', label: 'Invited' },
    { value: 'Interviewed', label: 'Interviewed' }, // Giữ lại Interviewed
    { value: 'Cancelled', label: 'Cancelled' }
  ];



  const dispatch = useAppDispatch();
  const [showResult, setShowResult] = useState(false);
  const resultOptions = [
    { label: 'Passed', value: 'Passed' },
    { label: 'Failed', value: 'Failed' }
  ];

  // Thêm watch cho status field
  const [form] = Form.useForm();
  const candidateValue = Form.useWatch('candidate_id', form);
  const statusValue = Form.useWatch('status', form);

  useEffect(() => {
    console.log('Watched candidate_id:', candidateValue);
    console.log('Watched status:', statusValue);
  }, [candidateValue, statusValue]);

  useEffect(() => {
    const status = form.getFieldValue('status');
    setShowResult(status === 'Interviewed');
  }, [form.getFieldValue('status')]);
  const handleFormSubmit = async (data) => {
    const selectedJobData = jobs.find(job => job.id === data.job_id.value || data.job_id);
    const { result, ...rest } = data;

    const payload = {
      ...rest,
      candidate_id: data.candidate_id.value || data.candidate_id,
      job_id: data.job_id.value || data.job_id,
      interviewer_ids: data.interviewer_ids.map((it: any) => it.value || it),
      position: selectedJobData?.position,
      status: data.status === 'Interviewed' ? data.result : data.status
    };

    // NEW: Update candidate status only on form submission
    if (initialValues && data.candidate_id) {
      const candidateId = data.candidate_id.value || data.candidate_id;
      let newStatus;

      if (data.status === 'Interviewed') {
        newStatus = data.result === 'Passed' ? 'Passed interview' : 'Banned';
      } else if (data.status === 'Invited') {
        newStatus = 'Waiting for interview';
      } else if (data.status === 'Cancelled') {
        newStatus = 'Cancelled interview';
      }

      await dispatch(updateCandidate({
        id: candidateId,
        payload: { status: newStatus }
      }));
    }

    if (initialValues) {
      await dispatch(updateInterview({ payload: payload, id: initialValues.id }));
    } else {
      await dispatch(createInterview(payload));
    }

    await dispatch(getInterviews({}));
    handleClose();
  };


  return (
    console.log('selectedCandidateId: ', selectedCandidateId),
    console.log('candidateValue: ', candidateValue),
    <Modal
      title={initialValues ? "EDIT INTERVIEW SCHEDULE" : "ADD INTERVIEW SCHEDULE"}
      open={isOpen}
      onOk={() => { }}
      onCancel={handleClose}
      footer={[]}
      className="text-xl"
      width={1000}
      key={initialValues}
    >
      <Form
        name="layout-multiple-horizontal"
        layout="horizontal"
        className="w-full mt-10"
        onFinish={handleFormSubmit}
        initialValues={initialValues || { status: 'Invited' }}
        labelCol={{ span: 6 }}
        key={initialValues}
        disabled={isDisable}
      >
        <div className="w-full flex justify-between">
          <Form.Item
            name="title"
            label="Interview title:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter schedule title' }]}
          >
            <Input
              allowClear
              placeholder={"Enter interview title"}
            />
          </Form.Item>

        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="job_id"
            label="Job title:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter job' }]}
          >
            <Select
              options={jobOptions}
              data-testid="select-interview-job"
              onChange={(value) => setSelectedJob(value)}

            />
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="candidate_id"
            label="Candidate:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter candidate name' }]}
          >
            <Select
              options={filteredCandidates}
              data-testid="select-interview-candidate"
              data-value={selectedCandidateId?.label || ''}
              placeholder="Select candidate"
              showSearch
              onChange={(value) => setSelectedCandidateId(value)}
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              notFoundContent="No candidate found"
            />
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="interviewer_ids"
            label="Interviewers:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter interviews' }]}
          >
            <Select
              data-testid="select-interview-interviewers"
              options={filteredUsers} mode="multiple" />
          </Form.Item>
          <Form.Item
            name="location"
            label="Location:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter location' }]}
          >
            <Input
              allowClear
              placeholder={"Enter location"}
            />
          </Form.Item>
        </div>
        <Form.Item
          name="schedule_date"
          label="Date:"
          labelCol={{ span: 3 }}
          rules={[{ required: true, message: 'Please enter date' }]}
        >
          <DatePicker
            data-testid="date-interview-schedule"
            className="w-full"
            disabledDate={(current) => current && current < moment().startOf('day')}
          />
        </Form.Item>
        <div className="w-full flex justify-between">
          <Form.Item
            name="schedule_time_to"
            label="From:"
            className="w-1/2 mr-5"
            rules={[{ required: true, message: 'Please enter time' }]}
          >
            <TimePicker
              data-testid="time-interview-from"
              className="w-full" />
          </Form.Item>
          <Form.Item
            name="schedule_time_from"
            label="To:"
            className="w-1/2"
            rules={[{ required: true, message: 'Please enter time' }]}
          >
            <TimePicker
              data-testid="time-interview-to"
              className="w-full" />
          </Form.Item>
        </div>
        <div className="w-full flex justify-between">
          <Form.Item
            name="status"
            label="Status:"
            // className="w-1/2"
            className="w-1/3 mr-5"
            rules={[{ required: true, message: 'Please enter status' }]}
          >
            <Select
              data-testid="select-interview-status"
              options={statusOptions}
              onChange={(value) => {
                setShowResult(value === 'Interviewed');
              }}


            />
          </Form.Item>
          {showResult && (
            <Form.Item
              name="result"
              label="Result:"
              className="w-1/3"
              rules={[{ required: true, message: 'Please select result' }]}
            >
              <Select
                data-testid="select-result"
                options={resultOptions}
              />
            </Form.Item>
          )}
          <Form.Item
            name="note"
            label="Note:"
            className="w-1/2"
          >
            <Input
              allowClear
              placeholder={"Enter note"}
            />
          </Form.Item>
        </div>
        <div className="w-full flex justify-end gap-x-5 mt-5">
          <Form.Item>
            <button
              className="border-blue-500 border px-4 py-2 text-blue-500 rounded"
              onClick={handleClose}
              type="button"
            >
              Close
            </button>
          </Form.Item>
          <Form.Item>
            <button
              className="bg-blue-500 hover:bg-blue-700 text-white py-2 px-5 rounded disabled:bg-gray-300 disabled:text-gray-500"
              type="submit"
            >
              Submit
            </button>
          </Form.Item>
        </div>
      </Form>
    </Modal>
  )
}
