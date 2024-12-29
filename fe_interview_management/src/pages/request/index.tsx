import Helmet from "@/components/Helmet.tsx";
import { Button, Input, Select, message, App } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import GenericTable from "@/components/Table";
import { useEffect, useState } from "react";
import { ModalAddRequest } from "@/components/modal/ModalAddRequest.tsx";
import { useAppDispatch, useAppSelector, useAuth } from "@/redux/hooks.ts";
import { createRequest, getRequests, updateRequest } from "@/redux/features/requestSlice.ts";
import moment from "moment";
import dayjs from "dayjs";
import axios from "axios";
import { notification } from 'antd';
// Constants for select options
const RequestStatus = {
    PENDING: 'Pending',
    APPROVED: 'Approved',
    REJECTED: 'Rejected'
};

const LevelOptions = [
    'Fresher',
    'Junior',
    'Senior',
    'Lead',
    'Manager'
];

const WorkplaceOptions = [
    'Ha Noi',
    'Hai Phong',
    'Ho Chi Minh',
    'Da Nang'
];



export const RequestPage = () => {
    const [selectedStatus, setSelectedStatus] = useState<any>(undefined);
    const [selectedRequest, setSelectedRequest] = useState<any>(undefined);
    const dispatch = useAppDispatch();
    const [isModalVisible, setIsModalVisible] = useState(false);
    const [requests, setRequests] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const { message: messageApi } = App.useApp();
    const columns = [
        {
            title: "CODE",
            dataIndex: "id",
            key: "id",
            render: (id: number) => "RQ" + id,
        },

        {
            title: 'Position',
            dataIndex: 'position',
            key: 'position',
        },
        {
            title: 'Quantity',
            dataIndex: 'quantity',
            key: 'quantity',
        },
        {
            title: 'Department',
            dataIndex: 'department',
            key: 'department',
        },
        {
            title: 'Level',
            dataIndex: 'level',
            key: 'level',
            render: (levels: string[]) => levels.join(', ')
        },
        {
            title: 'Workplace',
            dataIndex: 'workplace',
            key: 'workplace',
        },
        {
            title: 'Recruitment Period',
            key: 'recruitment_period',
            render: (record: any) => (
                `${moment(record.start_date).format('DD/MM/YYYY')} - 
                 ${moment(record.end_date).format('DD/MM/YYYY')}`
            )
        },
        {
            title: 'Status',
            dataIndex: 'status',
            key: 'status',
            render: (status: string, record: any) => (
                <div className="flex items-center gap-2">
                    <span className={`px-2 py-1 rounded-full ${getStatusColor(status)}`}>
                        {status}
                    </span>
                    {status === RequestStatus.PENDING &&
                        (user?.role === 'Admin' || user?.role === 'HR') && (
                            <Select
                                size="small"
                                style={{ width: 120 }}
                                placeholder="Change status"
                                onChange={(value) => handleStatusChange(record.id, value)}
                                onClick={(e) => e.stopPropagation()}
                            >
                                <Select.Option value={RequestStatus.APPROVED}>Approve</Select.Option>
                                <Select.Option value={RequestStatus.REJECTED}>Reject</Select.Option>
                            </Select>
                        )}
                </div>
            ),
        },
        {
            title: 'Created By',
            dataIndex: ['created_by', 'full_name'], // Nested access
            key: 'created_by',
        },

    ];
    const { role, user } = useAuth();

    const statusOptions = Object.entries(RequestStatus).map(([key, value]) => ({
        label: value,
        value: value
    }));

    const fetchRequests = async (search?: string) => {
        try {
            setLoading(true);
            const response = await axios.get('http://103.56.158.135:8086/api/v1/request', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Accept': 'application/json'
                },
                params: {
                    search,
                    filter: selectedStatus ? JSON.stringify({ status: selectedStatus }) : undefined
                }
            });
            setRequests(response.data.data.results);
            console.log(response.data.data.results);
        } catch (error) {
            console.error('Error fetching requests:', error);
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        fetchRequests();
    }, [selectedStatus]);


    useEffect(() => {
        dispatch(getRequests({}));
    }, [dispatch, selectedStatus]);


    const handleClose = () => {
        setSelectedRequest(undefined);
        setIsModalVisible(false);
        fetchRequests(); // Refresh data after modal closes
    };

    const handleSearch = (search: string) => {
        fetchRequests(search);
    };


    useEffect(() => {
        handleSearch('');
    }, [selectedStatus]);

    // Function to generate Request ID
    const generateRequestId = (workplace: string, position: string, currentCount: number) => {
        const prefix = workplace.split(' ').map(word => word[0]).join('');
        const formattedCount = String(currentCount).padStart(2, '0');
        return `${prefix}-${position}-${formattedCount}`;
    };
    const handleStatusChange = async (id: number, newStatus: string) => {
        try {
            setLoading(true);
            await axios.patch(
                `http://103.56.158.135:8086/api/v1/request/${id}/status`,
                { status: newStatus },
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    }
                }
            );

            // Update local state trước khi gọi fetch
            setRequests(prevRequests =>
                prevRequests.map(request =>
                    request.id === id
                        ? { ...request, status: newStatus }
                        : request
                )
            );

            // Fetch lại data để đồng bộ
            await fetchRequests();
        } catch (error) {
            console.error('Error updating request status:', error);
            messageApi.error('Failed to update request status');
        } finally {
            setLoading(false);
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case RequestStatus.PENDING:
                return 'bg-yellow-100 text-yellow-800 border border-yellow-200';
            case RequestStatus.APPROVED:
                return 'bg-green-100 text-green-800 border border-green-200';
            case RequestStatus.REJECTED:
                return 'bg-red-100 text-red-800 border border-red-200';
            default:
                return '';
        }
    };


    const handleCreateRequest = async (values: any) => {
        try {
            await axios.post('http://103.56.158.135:8086/api/v1/request', values, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });

            fetchRequests(); // Refresh data after creation
            handleClose();
        } catch (error) {
            console.error('Error creating request:', error);
        }
    };


    return (
        <div className="p-10 bg-white h-full rounded">
            <Helmet title="Manage Recruitment Requests" />
            <ModalAddRequest
                isOpen={isModalVisible}
                handleClose={handleClose}
                initialValues={selectedRequest}
                key={selectedRequest}
                onSubmit={handleCreateRequest}
            />
            <div className="w-full flex justify-between items-center">
                <div className="flex w-9/12">
                    <Select
                        className="w-1/6 mr-2"
                        placeholder="Select status"
                        options={statusOptions}
                        onChange={(value) => setSelectedStatus(value)}
                        size="large"
                        defaultValue={selectedStatus}
                        allowClear
                    />
                    <Input.Search
                        className="w-1/3"
                        placeholder="Search by position or ID"
                        onSearch={handleSearch}
                        size="large"
                    />
                </div>
                <Button
                    className="bg-blue-500 text-white p-5 rounded-lg"
                    icon={<PlusOutlined />}
                    onClick={() => setIsModalVisible(true)}
                >
                    New Recruitment Request
                </Button>
            </div>
            <div className="mt-5">
                <GenericTable
                    columns={columns}
                    data={requests}
                    loading={loading}
                    onDeleteItem={async (record) => {
                        try {
                            await axios.delete(`http://103.56.158.135:8086/api/v1/request/${record.id}`, {
                                headers: {
                                    'Authorization': `Bearer ${localStorage.getItem('token')}`
                                }
                            });
                            notification.success({
                                message: 'Request deleted successfully',
                                description: `The request has been successfully deleted.`,
                                placement: 'topRight',
                            });

                            fetchRequests();
                        } catch (error) {
                            console.error('Error deleting request:', error);
                            notification.error({
                                message: 'Failed to delete request',
                                description: 'There was an error deleting the request.',
                                placement: 'topRight',
                            });
                        }
                    }}
                    onEditItem={(record) => {
                        setSelectedRequest({
                            ...record,
                            start_date: dayjs(record.start_date),
                            end_date: dayjs(record.end_date)
                        });
                        setIsModalVisible(true);
                    }}
                />
            </div>
        </div>
    );
};

export default RequestPage;
