import { DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { Button, Popconfirm, Space, Table, TablePaginationConfig, TableProps } from 'antd';
import { ColumnsType } from 'antd/es/table';
import { useAuth } from "@/redux/hooks.ts";
interface GenericTableProps<T> {
  columns: ColumnsType<T>;
  data: T[];
  onEditItem?: (record: T) => void;
  onDeleteItem?: (record: T) => void;
  className?: string;
  enableAction?: boolean;
  pagination?: TablePaginationConfig,
  enableSelection?: boolean;
  onSelectionChange?: (selectedRowKeys: React.Key[], selectedRows: T[]) => void;
  showAction?: boolean;
}

const GenericTable = <T extends {}>({
  columns,
  data,
  onEditItem,
  onDeleteItem,
  className,
  enableAction = true,
  pagination,
  enableSelection,
  onSelectionChange,
  showAction = true,
}: GenericTableProps<T>) => {
  const { role } = useAuth();

  const actionColumn = showAction ? [
    {
      title: 'Actions',
      key: 'actions',
      fixed: 'right',
      width: 100,
      render: (_text: string, record: T) => (
        <Space size="middle">
          {
            onEditItem && role !== 'Interviewer' &&
            <Button key="edit" data-testid-edit={record.id} className="border border-blue-400 text-blue-400" onClick={() => onEditItem(record)}>
              <EditOutlined />
            </Button>
          }
          {
            onDeleteItem && role == 'Admin' &&
            <Popconfirm
              id={'delete'}
              title="Delete the task"
              description="Are you sure to delete this task?"
              okText="Yes"
              cancelText="No"
              placement="leftTop"
              okButtonProps={{ type: 'primary', danger: true }}
              onConfirm={(e) => {
                e?.stopPropagation();
                onDeleteItem(record);
              }}
              onCancel={(e) => {
                e?.stopPropagation();
              }}
            >
              <Button data-testid={record.id} key="delete" danger id="delete" onClick={(e) => {
                e.stopPropagation(); // Ensure row click event is not triggered
              }}>
                <DeleteOutlined id="ic_delete" />
              </Button>
            </Popconfirm>
          }
        </Space>
      ),
    },
  ] : []

  const indexedColumns = [
    {
      title: 'No.',
      dataIndex: 'index',
      key: 'index',
      render: (_text: string, _record: T, index: number) => index + 1,
    },
    ...columns,
    ...(enableAction ? actionColumn : []),
  ];

  const rowSelection: TableProps<T>['rowSelection'] = {
    onChange: (selectedRowKeys: React.Key[], selectedRows: T[]) => {
      onSelectionChange && onSelectionChange(selectedRowKeys, selectedRows);
    },
    getCheckboxProps: (record: T) => ({
      //@ts-ignore
      name: record?.id
    }),
  };

  return (
    console.log('role: ', role),
    <Table
      scroll={{ x: 'max-content' }}
      className={className}
      // @ts-ignore
      columns={indexedColumns}
      dataSource={data}
      rowKey="id"
      pagination={{ showSizeChanger: true, pageSizeOptions: ['10', '20', '30', '40', '50'], defaultPageSize: 10 } as any}
      onRow={(record, rowIndex) => {
        return {
          onClick: (event) => {
            onEditItem && onEditItem(record);
          },
        };
      }}
      rowClassName="cursor-pointer"
      rowSelection={enableSelection ? { type: 'checkbox', ...rowSelection } : undefined}
    />
  );
};

export default GenericTable;
