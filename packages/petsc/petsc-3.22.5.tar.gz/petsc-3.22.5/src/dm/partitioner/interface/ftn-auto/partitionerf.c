#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* partitioner.c */
/* Fortran interface file */

/*
* This file was generated automatically by bfort from the C source
* file.  
 */

#ifdef PETSC_USE_POINTER_CONVERSION
#if defined(__cplusplus)
extern "C" { 
#endif 
extern void *PetscToPointer(void*);
extern int PetscFromPointer(void *);
extern void PetscRmPointer(void*);
#if defined(__cplusplus)
} 
#endif 

#else

#define PetscToPointer(a) (a ? *(PetscFortranAddr *)(a) : 0)
#define PetscFromPointer(a) (PetscFortranAddr)(a)
#define PetscRmPointer(a)
#endif

#include "petscpartitioner.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionersettype_ PETSCPARTITIONERSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionersettype_ petscpartitionersettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionergettype_ PETSCPARTITIONERGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionergettype_ petscpartitionergettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionerviewfromoptions_ PETSCPARTITIONERVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionerviewfromoptions_ petscpartitionerviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionerview_ PETSCPARTITIONERVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionerview_ petscpartitionerview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionersetfromoptions_ PETSCPARTITIONERSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionersetfromoptions_ petscpartitionersetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionersetup_ PETSCPARTITIONERSETUP
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionersetup_ petscpartitionersetup
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionerreset_ PETSCPARTITIONERRESET
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionerreset_ petscpartitionerreset
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionerdestroy_ PETSCPARTITIONERDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionerdestroy_ petscpartitionerdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionerpartition_ PETSCPARTITIONERPARTITION
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionerpartition_ petscpartitionerpartition
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define petscpartitionercreate_ PETSCPARTITIONERCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define petscpartitionercreate_ petscpartitionercreate
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  petscpartitionersettype_(PetscPartitioner part,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(part);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscPartitionerSetType(
	(PetscPartitioner)PetscToPointer((part) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscpartitionergettype_(PetscPartitioner part,char *name, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerGetType(
	(PetscPartitioner)PetscToPointer((part) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for name */
*ierr = PetscStrncpy(name, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, name, cl0);
}
PETSC_EXTERN void  petscpartitionerviewfromoptions_(PetscPartitioner A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = PetscPartitionerViewFromOptions(
	(PetscPartitioner)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  petscpartitionerview_(PetscPartitioner part,PetscViewer v, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLOBJECT(v);
*ierr = PetscPartitionerView(
	(PetscPartitioner)PetscToPointer((part) ),PetscPatchDefaultViewers((PetscViewer*)v));
}
PETSC_EXTERN void  petscpartitionersetfromoptions_(PetscPartitioner part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerSetFromOptions(
	(PetscPartitioner)PetscToPointer((part) ));
}
PETSC_EXTERN void  petscpartitionersetup_(PetscPartitioner part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerSetUp(
	(PetscPartitioner)PetscToPointer((part) ));
}
PETSC_EXTERN void  petscpartitionerreset_(PetscPartitioner part, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerReset(
	(PetscPartitioner)PetscToPointer((part) ));
}
PETSC_EXTERN void  petscpartitionerdestroy_(PetscPartitioner *part, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(part);
 PetscBool part_null = !*(void**) part ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerDestroy(part);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! part_null && !*(void**) part) * (void **) part = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(part);
 }
PETSC_EXTERN void  petscpartitionerpartition_(PetscPartitioner part,PetscInt *nparts,PetscInt *numVertices,PetscInt start[],PetscInt adjacency[],PetscSection vertexSection,PetscSection edgeSection,PetscSection targetSection,PetscSection partSection,IS *partition, int *ierr)
{
CHKFORTRANNULLOBJECT(part);
CHKFORTRANNULLINTEGER(start);
CHKFORTRANNULLINTEGER(adjacency);
CHKFORTRANNULLOBJECT(vertexSection);
CHKFORTRANNULLOBJECT(edgeSection);
CHKFORTRANNULLOBJECT(targetSection);
CHKFORTRANNULLOBJECT(partSection);
PetscBool partition_null = !*(void**) partition ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(partition);
*ierr = PetscPartitionerPartition(
	(PetscPartitioner)PetscToPointer((part) ),*nparts,*numVertices,start,adjacency,
	(PetscSection)PetscToPointer((vertexSection) ),
	(PetscSection)PetscToPointer((edgeSection) ),
	(PetscSection)PetscToPointer((targetSection) ),
	(PetscSection)PetscToPointer((partSection) ),partition);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! partition_null && !*(void**) partition) * (void **) partition = (void *)-2;
}
PETSC_EXTERN void  petscpartitionercreate_(MPI_Fint * comm,PetscPartitioner *part, int *ierr)
{
PETSC_FORTRAN_OBJECT_CREATE(part);
 PetscBool part_null = !*(void**) part ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(part);
*ierr = PetscPartitionerCreate(
	MPI_Comm_f2c(*(comm)),part);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! part_null && !*(void**) part) * (void **) part = (void *)-2;
}
#if defined(__cplusplus)
}
#endif
