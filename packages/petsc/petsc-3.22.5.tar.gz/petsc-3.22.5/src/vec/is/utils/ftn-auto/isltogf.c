#include "petscsys.h"
#include "petscfix.h"
#include "petsc/private/fortranimpl.h"
/* isltog.c */
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

#include "petscis.h"
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isgetpointsubrange_ ISGETPOINTSUBRANGE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isgetpointsubrange_ isgetpointsubrange
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingduplicate_ ISLOCALTOGLOBALMAPPINGDUPLICATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingduplicate_ islocaltoglobalmappingduplicate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappinggetsize_ ISLOCALTOGLOBALMAPPINGGETSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappinggetsize_ islocaltoglobalmappinggetsize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingviewfromoptions_ ISLOCALTOGLOBALMAPPINGVIEWFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingviewfromoptions_ islocaltoglobalmappingviewfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingview_ ISLOCALTOGLOBALMAPPINGVIEW
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingview_ islocaltoglobalmappingview
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingload_ ISLOCALTOGLOBALMAPPINGLOAD
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingload_ islocaltoglobalmappingload
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingcreateis_ ISLOCALTOGLOBALMAPPINGCREATEIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingcreateis_ islocaltoglobalmappingcreateis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingcreatesf_ ISLOCALTOGLOBALMAPPINGCREATESF
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingcreatesf_ islocaltoglobalmappingcreatesf
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingsetblocksize_ ISLOCALTOGLOBALMAPPINGSETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingsetblocksize_ islocaltoglobalmappingsetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappinggetblocksize_ ISLOCALTOGLOBALMAPPINGGETBLOCKSIZE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappinggetblocksize_ islocaltoglobalmappinggetblocksize
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingcreate_ ISLOCALTOGLOBALMAPPINGCREATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingcreate_ islocaltoglobalmappingcreate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingsetfromoptions_ ISLOCALTOGLOBALMAPPINGSETFROMOPTIONS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingsetfromoptions_ islocaltoglobalmappingsetfromoptions
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingdestroy_ ISLOCALTOGLOBALMAPPINGDESTROY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingdestroy_ islocaltoglobalmappingdestroy
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingapplyis_ ISLOCALTOGLOBALMAPPINGAPPLYIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingapplyis_ islocaltoglobalmappingapplyis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingapply_ ISLOCALTOGLOBALMAPPINGAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingapply_ islocaltoglobalmappingapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingapplyblock_ ISLOCALTOGLOBALMAPPINGAPPLYBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingapplyblock_ islocaltoglobalmappingapplyblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isglobaltolocalmappingapply_ ISGLOBALTOLOCALMAPPINGAPPLY
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isglobaltolocalmappingapply_ isglobaltolocalmappingapply
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isglobaltolocalmappingapplyis_ ISGLOBALTOLOCALMAPPINGAPPLYIS
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isglobaltolocalmappingapplyis_ isglobaltolocalmappingapplyis
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define isglobaltolocalmappingapplyblock_ ISGLOBALTOLOCALMAPPINGAPPLYBLOCK
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define isglobaltolocalmappingapplyblock_ isglobaltolocalmappingapplyblock
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingconcatenate_ ISLOCALTOGLOBALMAPPINGCONCATENATE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingconcatenate_ islocaltoglobalmappingconcatenate
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappingsettype_ ISLOCALTOGLOBALMAPPINGSETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappingsettype_ islocaltoglobalmappingsettype
#endif
#ifdef PETSC_HAVE_FORTRAN_CAPS
#define islocaltoglobalmappinggettype_ ISLOCALTOGLOBALMAPPINGGETTYPE
#elif !defined(PETSC_HAVE_FORTRAN_UNDERSCORE) && !defined(FORTRANDOUBLEUNDERSCORE)
#define islocaltoglobalmappinggettype_ islocaltoglobalmappinggettype
#endif
/* Provide declarations for malloc/free if needed for strings */
#include <stdlib.h>


/* Definitions of Fortran Wrapper routines */
#if defined(__cplusplus)
extern "C" {
#endif
PETSC_EXTERN void  isgetpointsubrange_(IS subpointIS,PetscInt *pStart,PetscInt *pEnd, PetscInt points[], int *ierr)
{
CHKFORTRANNULLOBJECT(subpointIS);
CHKFORTRANNULLINTEGER(points);
*ierr = ISGetPointSubrange(
	(IS)PetscToPointer((subpointIS) ),*pStart,*pEnd,points);
}
PETSC_EXTERN void  islocaltoglobalmappingduplicate_(ISLocalToGlobalMapping ltog,ISLocalToGlobalMapping *nltog, int *ierr)
{
CHKFORTRANNULLOBJECT(ltog);
PetscBool nltog_null = !*(void**) nltog ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(nltog);
*ierr = ISLocalToGlobalMappingDuplicate(
	(ISLocalToGlobalMapping)PetscToPointer((ltog) ),nltog);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! nltog_null && !*(void**) nltog) * (void **) nltog = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappinggetsize_(ISLocalToGlobalMapping mapping,PetscInt *n, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(n);
*ierr = ISLocalToGlobalMappingGetSize(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),n);
}
PETSC_EXTERN void  islocaltoglobalmappingviewfromoptions_(ISLocalToGlobalMapping A,PetscObject obj, char name[], int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(A);
CHKFORTRANNULLOBJECT(obj);
/* insert Fortran-to-C conversion for name */
  FIXCHAR(name,cl0,_cltmp0);
*ierr = ISLocalToGlobalMappingViewFromOptions(
	(ISLocalToGlobalMapping)PetscToPointer((A) ),
	(PetscObject)PetscToPointer((obj) ),_cltmp0);
  FREECHAR(name,_cltmp0);
}
PETSC_EXTERN void  islocaltoglobalmappingview_(ISLocalToGlobalMapping mapping,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLOBJECT(viewer);
*ierr = ISLocalToGlobalMappingView(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  islocaltoglobalmappingload_(ISLocalToGlobalMapping mapping,PetscViewer viewer, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLOBJECT(viewer);
*ierr = ISLocalToGlobalMappingLoad(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),PetscPatchDefaultViewers((PetscViewer*)viewer));
}
PETSC_EXTERN void  islocaltoglobalmappingcreateis_(IS is,ISLocalToGlobalMapping *mapping, int *ierr)
{
CHKFORTRANNULLOBJECT(is);
PetscBool mapping_null = !*(void**) mapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingCreateIS(
	(IS)PetscToPointer((is) ),mapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mapping_null && !*(void**) mapping) * (void **) mapping = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappingcreatesf_(PetscSF sf,PetscInt *start,ISLocalToGlobalMapping *mapping, int *ierr)
{
CHKFORTRANNULLOBJECT(sf);
PetscBool mapping_null = !*(void**) mapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingCreateSF(
	(PetscSF)PetscToPointer((sf) ),*start,mapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mapping_null && !*(void**) mapping) * (void **) mapping = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappingsetblocksize_(ISLocalToGlobalMapping mapping,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingSetBlockSize(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*bs);
}
PETSC_EXTERN void  islocaltoglobalmappinggetblocksize_(ISLocalToGlobalMapping mapping,PetscInt *bs, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(bs);
*ierr = ISLocalToGlobalMappingGetBlockSize(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),bs);
}
PETSC_EXTERN void  islocaltoglobalmappingcreate_(MPI_Fint * comm,PetscInt *bs,PetscInt *n, PetscInt indices[],PetscCopyMode *mode,ISLocalToGlobalMapping *mapping, int *ierr)
{
CHKFORTRANNULLINTEGER(indices);
PetscBool mapping_null = !*(void**) mapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingCreate(
	MPI_Comm_f2c(*(comm)),*bs,*n,indices,*mode,mapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mapping_null && !*(void**) mapping) * (void **) mapping = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappingsetfromoptions_(ISLocalToGlobalMapping mapping, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingSetFromOptions(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ));
}
PETSC_EXTERN void  islocaltoglobalmappingdestroy_(ISLocalToGlobalMapping *mapping, int *ierr)
{
PETSC_FORTRAN_OBJECT_F_DESTROYED_TO_C_NULL(mapping);
 PetscBool mapping_null = !*(void**) mapping ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(mapping);
*ierr = ISLocalToGlobalMappingDestroy(mapping);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! mapping_null && !*(void**) mapping) * (void **) mapping = (void *)-2;
if (*ierr) return;
PETSC_FORTRAN_OBJECT_C_NULL_TO_F_DESTROYED(mapping);
 }
PETSC_EXTERN void  islocaltoglobalmappingapplyis_(ISLocalToGlobalMapping mapping,IS is,IS *newis, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLOBJECT(is);
PetscBool newis_null = !*(void**) newis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newis);
*ierr = ISLocalToGlobalMappingApplyIS(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),
	(IS)PetscToPointer((is) ),newis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newis_null && !*(void**) newis) * (void **) newis = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappingapply_(ISLocalToGlobalMapping mapping,PetscInt *N, PetscInt in[],PetscInt out[], int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(in);
CHKFORTRANNULLINTEGER(out);
*ierr = ISLocalToGlobalMappingApply(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*N,in,out);
}
PETSC_EXTERN void  islocaltoglobalmappingapplyblock_(ISLocalToGlobalMapping mapping,PetscInt *N, PetscInt in[],PetscInt out[], int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(in);
CHKFORTRANNULLINTEGER(out);
*ierr = ISLocalToGlobalMappingApplyBlock(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*N,in,out);
}
PETSC_EXTERN void  isglobaltolocalmappingapply_(ISLocalToGlobalMapping mapping,ISGlobalToLocalMappingMode *type,PetscInt *n, PetscInt idx[],PetscInt *nout,PetscInt idxout[], int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(idx);
CHKFORTRANNULLINTEGER(nout);
CHKFORTRANNULLINTEGER(idxout);
*ierr = ISGlobalToLocalMappingApply(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*type,*n,idx,nout,idxout);
}
PETSC_EXTERN void  isglobaltolocalmappingapplyis_(ISLocalToGlobalMapping mapping,ISGlobalToLocalMappingMode *type,IS is,IS *newis, int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLOBJECT(is);
PetscBool newis_null = !*(void**) newis ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(newis);
*ierr = ISGlobalToLocalMappingApplyIS(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*type,
	(IS)PetscToPointer((is) ),newis);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! newis_null && !*(void**) newis) * (void **) newis = (void *)-2;
}
PETSC_EXTERN void  isglobaltolocalmappingapplyblock_(ISLocalToGlobalMapping mapping,ISGlobalToLocalMappingMode *type,PetscInt *n, PetscInt idx[],PetscInt *nout,PetscInt idxout[], int *ierr)
{
CHKFORTRANNULLOBJECT(mapping);
CHKFORTRANNULLINTEGER(idx);
CHKFORTRANNULLINTEGER(nout);
CHKFORTRANNULLINTEGER(idxout);
*ierr = ISGlobalToLocalMappingApplyBlock(
	(ISLocalToGlobalMapping)PetscToPointer((mapping) ),*type,*n,idx,nout,idxout);
}
PETSC_EXTERN void  islocaltoglobalmappingconcatenate_(MPI_Fint * comm,PetscInt *n, ISLocalToGlobalMapping ltogs[],ISLocalToGlobalMapping *ltogcat, int *ierr)
{
PetscBool ltogs_null = !*(void**) ltogs ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ltogs);
PetscBool ltogcat_null = !*(void**) ltogcat ? PETSC_TRUE : PETSC_FALSE;
CHKFORTRANNULLOBJECT(ltogcat);
*ierr = ISLocalToGlobalMappingConcatenate(
	MPI_Comm_f2c(*(comm)),*n,ltogs,ltogcat);
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ltogs_null && !*(void**) ltogs) * (void **) ltogs = (void *)-2;
// if C routine nullifed the object, we must set to to -2 to indicate null set in Fortran
if (! ltogcat_null && !*(void**) ltogcat) * (void **) ltogcat = (void *)-2;
}
PETSC_EXTERN void  islocaltoglobalmappingsettype_(ISLocalToGlobalMapping ltog,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ltog);
/* insert Fortran-to-C conversion for type */
  FIXCHAR(type,cl0,_cltmp0);
*ierr = ISLocalToGlobalMappingSetType(
	(ISLocalToGlobalMapping)PetscToPointer((ltog) ),_cltmp0);
  FREECHAR(type,_cltmp0);
}
PETSC_EXTERN void  islocaltoglobalmappinggettype_(ISLocalToGlobalMapping ltog,char *type, int *ierr, PETSC_FORTRAN_CHARLEN_T cl0)
{
  char *_cltmp0 = PETSC_NULLPTR;
CHKFORTRANNULLOBJECT(ltog);
*ierr = ISLocalToGlobalMappingGetType(
	(ISLocalToGlobalMapping)PetscToPointer((ltog) ),(const char **)&_cltmp0);
/* insert C-to-Fortran conversion for type */
*ierr = PetscStrncpy(type, _cltmp0, cl0);
                        if (*ierr) return;
                        FIXRETURNCHAR(PETSC_TRUE, type, cl0);
}
#if defined(__cplusplus)
}
#endif
